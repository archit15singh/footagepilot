import copy,json,tempfile,unittest
from pathlib import Path
from footagepilot.framing import options_for,choose_crops,refine_framing


class FramingTests(unittest.TestCase):
    def evidence(self):return [{'shot':2,'options':options_for({'focus_x':.51,'focus_y':.43},'y')}]
    def choice(self):return {'choices':[{'shot':2,'option':'option-4','reason':'Retains head across samples','uncertainty':'No continuous tracking'}]}

    def test_refinement_changes_only_selected_focus_and_keeps_edit_structure(self):
        data={'shots':[{'path':'a','duration':2,'focus_y':.5},{'path':'b','source_start':2.3,'duration':1.63,'focus_x':.51,'focus_y':.43,'fit':'fill','zoom':0}], 'titles':[{'text':'Title'}],'music':'score','transitions':[{'after_shot':0,'duration':.1}],'music_timing':{'cues':[0,2,3.63]}}
        before=copy.deepcopy(data);revised=choose_crops(data,self.evidence(),self.choice())
        self.assertEqual(data,before)
        self.assertEqual(revised['shots'][1]['focus_y'],.73)
        revised['shots'][1]['focus_y']=.43
        self.assertEqual(revised,before)

    def test_unknown_duplicate_or_missing_choices_reject(self):
        choice=self.choice()['choices'][0]
        for choices in ([],[dict(choice,shot=1)],[dict(choice,option='shell command')],[choice,choice],[dict(choice,reason='')]):
            with self.assertRaises(ValueError):choose_crops({'shots':[{},{}]},self.evidence(),{'choices':choices})

    def test_alternatives_are_bounded_and_current_stays_exact(self):
        for current in (0,.333333333333,1):
            options=options_for({'focus_y':current},'y')
            self.assertEqual(options[0]['focus_y'],current)
            self.assertTrue(all(0<=o['focus_y']<=1 for o in options))
            self.assertEqual(len({o['focus_y'] for o in options}),len(options))
        for shot,axis in (({'fit':'contain'},'y'),({'zoom':.025},'x'),({},'z')):
            with self.assertRaises(ValueError):options_for(shot,axis)

    def test_bad_requests_do_not_create_output_or_call_model(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'source.jpg').touch();manifest=root/'edit.json';manifest.write_text(json.dumps({'shots':[{'path':'source.jpg','duration':1}]}))
            for shots in ([],[0],[1,1],[2],[True]):
                with self.assertRaises(ValueError):refine_framing(manifest,shots,'y',root/'output')
                self.assertFalse((root/'output').exists())

    def test_changed_source_rejects_model_choice_before_manifest_write(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'source.mp4';source.write_bytes(b'original');manifest=root/'edit.json';manifest.write_text(json.dumps({'shots':[{'path':'source.mp4','duration':1}]}));output=root/'refinement'
            def render(cmd):Path(cmd[-1]).write_bytes(b'jpeg')
            def model(cmd,**kwargs):
                Path(cmd[cmd.index('-o')+1]).write_text(json.dumps({'choices':[{'shot':1,'option':'option-0','reason':'Keep','uncertainty':'Three samples'}]}));source.write_bytes(b'changed');return SimpleNamespace(returncode=0,stderr='')
            with patch('footagepilot.framing.binary',return_value='ffmpeg'),patch('footagepilot.framing.probe',return_value={'streams':[{'codec_type':'video','duration':'2'}]}),patch('footagepilot.framing.run',side_effect=render),patch('footagepilot.framing.subprocess.run',side_effect=model):
                with self.assertRaisesRegex(ValueError,'evidence changed'):refine_framing(manifest,[1],'y',output)
            self.assertFalse((output/'edit.json').exists());self.assertTrue((output/'failure.json').exists())

    def test_evaluation_rejects_native_jobs_from_other_manifests(self):
        from evals.framing_refinement import evaluate
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);before=root/'before.json';after=root/'after.json'
            before.write_text(json.dumps({'shots':[{'path':'source.mp4','duration':1,'focus_y':.4}]}));after.write_text(json.dumps({'shots':[{'path':'source.mp4','duration':1,'focus_y':.7}]}))
            job=root/'job.json';job.write_text(json.dumps({'shots':[{'start':0,'frames':30}],'manifest_sha256':'wrong'}))
            with self.assertRaisesRegex(ValueError,'different manifest'):evaluate(before,after,job,job,root/'movie.mp4',root/'project.drp',root/'eval')
            self.assertFalse((root/'eval').exists())
