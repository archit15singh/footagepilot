import hashlib,json,tempfile,unittest
from pathlib import Path
from footagepilot.reference_rhythm import rhythm_options,extract_rhythm,validate_reference_timing
from footagepilot.visual import compile_plan

class ReferenceRhythmTests(unittest.TestCase):
    def setup_reference(self,root):
        music=root/'media.mp4';music.write_bytes(b'reference with audio');analysis=root/'analysis.json'
        analysis.write_text(json.dumps({'decode':'passed','source_sha256':hashlib.sha256(music.read_bytes()).hexdigest(),'duration':4,'scene_changes':[1.2,2.7,2.74,3.1,3.95]}));return analysis,music

    def test_exact_coordinates_gap_filtering_and_analysis_binding(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);analysis,music=self.setup_reference(root)
            result=extract_rhythm(analysis,music,root/'rhythm.json',4,.15);timing=result['music_timing']
            self.assertEqual(timing['cues'],[0,1.2,2.7,3.1,4]);self.assertEqual(result['omitted_close_candidates'],[2.74,3.95])
            validate_reference_timing(timing,analysis,music)
            with self.assertRaisesRegex(ValueError,'unsupported change'):validate_reference_timing({**timing,'cues':[0,1.21,2.7,3.1,4]},analysis,music)
            analysis.write_text(analysis.read_text()+'\n')
            with self.assertRaisesRegex(ValueError,'changed analysis'):validate_reference_timing(timing,analysis,music)
            with self.assertRaises(ValueError):extract_rhythm(analysis,music,root/'rhythm.json',4)

    def test_native_coordinate_check_rejects_shifted_or_wrong_mode_jobs(self):
        from evals.reference_rhythm import check_coordinates
        timing={'cues':[0,1.2,2.72,4.24]};job={'fps':30,'frames':127,'timing_mode':'reference_changes','shots':[{'start':0},{'start':36},{'start':82}]}
        self.assertEqual(check_coordinates(timing,job),[0,36,82,127])
        for changed in ({**job,'frames':128},{**job,'timing_mode':'onset_candidates'},{**job,'shots':[{'start':0},{'start':35},{'start':82}]}):
            with self.assertRaises(ValueError):check_coordinates(timing,changed)

    def test_changed_music_and_unordered_candidates_reject(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);analysis,music=self.setup_reference(root);music.write_bytes(b'other')
            with self.assertRaisesRegex(ValueError,'unchanged analyzed'):extract_rhythm(analysis,music,root/'bad.json',4)
            analysis,music=self.setup_reference(root);d=json.loads(analysis.read_text());d['scene_changes']=[2,1];analysis.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,'strictly ordered'):extract_rhythm(analysis,music,root/'bad.json',4)
            self.assertFalse((root/'bad.json').exists())

    def test_conflicting_requests_reject_before_work(self):
        spec={'reference_rhythm':{},'music_from_reference':True,'min_seconds':14,'max_seconds':14}
        self.assertEqual(rhythm_options(spec,'resolve'),{'duration':14,'min_gap':.15})
        for changes,backend in (({},'edits'),({'music_analysis':{}},'resolve'),({'music_timing':{}},'resolve'),({'music_from_reference':False},'resolve'),({'reference_rhythm':{'duration':12}},'resolve'),({'reference_rhythm':{'min_gap':float('nan')}},'resolve')):
            with self.assertRaises(ValueError):rhythm_options({**spec,**changes},backend)

    def test_compiler_cannot_merge_or_skip_reference_intervals(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);analysis,music=self.setup_reference(root);(root/'a.jpg').touch()
            timing=extract_rhythm(analysis,music,root/'rhythm.json',4)['music_timing']
            spec={'native_backend':'resolve','reference':str(analysis),'assets':[{'id':'a','path':'a.jpg'}],'music':str(music),'music_timing':timing,'min_seconds':4,'max_seconds':4,'show_titles':False}
            shot={'asset_id':'a','beats':1,'fit':'fill','zoom':0};plan={'title':'A trip','shots':[shot]*4,'panels':[],'backgrounds':[]}
            edit=compile_plan(plan,spec,root);self.assertEqual([round(s['duration'],3) for s in edit['shots']],[1.2,1.5,.4,.9])
            for rows in ([shot]*3,[{**shot,'beats':2}]+[shot]*3):
                with self.assertRaisesRegex(ValueError,'one shot per'):compile_plan({**plan,'shots':rows},spec,root)
