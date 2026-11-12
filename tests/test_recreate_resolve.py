import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from footagepilot.recreate import recreate,finish_resolve,reference_soundtrack

class ResolveRecreationTests(unittest.TestCase):
    def test_reference_audio_is_bound_to_analyzed_media(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);media=root/'media.mp4';media.write_bytes(b'analyzed source');analysis=root/'analysis.json'
            record={'decode':'passed','audio':{'present':True},'source_sha256':hashlib.sha256(media.read_bytes()).hexdigest()};analysis.write_text(json.dumps(record))
            self.assertEqual(reference_soundtrack(analysis)['media'],str(media.resolve()))
            media.write_bytes(b'replaced source')
            with self.assertRaisesRegex(ValueError,'changed since analysis'):reference_soundtrack(analysis)
            record['audio']['present']=False;analysis.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError,'with audio'):reference_soundtrack(analysis)

    def test_reference_audio_request_is_explicit_and_unambiguous(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec=root/'spec.json'
            for backend,extra in [('edits',{}),('resolve',{'music':'track.wav'}),('resolve',{'music_from_reference':False})]:
                spec.write_text(json.dumps({'music_from_reference':True,**extra}))
                with self.assertRaisesRegex(ValueError,'music_from_reference=true'):recreate(spec,root/'run',backend=backend)
                self.assertFalse((root/'run').exists())

    def test_music_request_cannot_override_timing_or_open_edits(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec=root/'spec.json'
            for backend,extra,message in [('edits',{},'requires Resolve'),('resolve',{'music_timing':{}},'not both'),('resolve',{'music_analysis':{'max_duration':2},'max_seconds':14},'cover max_seconds')]:
                spec.write_text(json.dumps({'music_analysis':{},**extra}))
                with self.assertRaisesRegex(ValueError,message):recreate(spec,root/'run',backend=backend)
                self.assertFalse((root/'run').exists())

    def test_failed_music_analysis_stops_before_planning_and_is_retained(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec=root/'spec.json';spec.write_text(json.dumps({'reference':'ref.json','assets':[],'music':'track.wav','music_analysis':{},'max_seconds':14}))
            with patch('footagepilot.recreate.check_sources',return_value={'needs_research':False}),patch('footagepilot.recreate.extract_cues',side_effect=ValueError('no usable audio cues')),patch('footagepilot.recreate.plan_visual') as planner:
                with self.assertRaisesRegex(ValueError,'no usable audio'):recreate(spec,root/'run',backend='resolve')
                planner.assert_not_called()
            state=json.loads((root/'run/run.json').read_text());self.assertFalse(state['passed']);self.assertEqual(state['stages'][-1]['status'],'failed')

    def test_measured_coordinates_reach_plan_without_manual_copy(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec=root/'spec.json';spec.write_text(json.dumps({'reference':'ref.json','assets':[],'music':'track.wav','music_analysis':{},'max_seconds':14}))
            timing={'mode':'onset_candidates','cues':[0,.7,14],'source_sha256':'a'*64,'provenance':'measured, not beats'}
            (root/'job.json').write_text('{}')
            def planner(path,output):
                local=json.loads(path.read_text());self.assertEqual(local['music_timing'],timing);self.assertNotIn('music_analysis',local)
                return {'manifest':str(root/'edit.json')}
            with patch('footagepilot.recreate.check_sources',return_value={'needs_research':False}),patch('footagepilot.recreate.extract_cues',return_value={'duration':14,'music_timing':timing}) as extractor,patch('footagepilot.recreate.plan_visual',side_effect=planner),patch('footagepilot.resolve.prepare',return_value={'job':str(root/'job.json'),'console':'console.lua'}):
                result=recreate(spec,root/'run',backend='resolve')
            self.assertFalse(result['passed']);self.assertEqual(result['stages'][1]['name'],'analyze-selected-music');self.assertEqual(extractor.call_args.kwargs['max_duration'],14)

    def test_prepared_native_run_is_not_marked_complete(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec=root/'spec.json';spec.write_text(json.dumps({'reference':'reference.json','assets':[],'music':'music.wav'}))
            (root/'native').mkdir();(root/'native/job.json').write_text('{}')
            with patch('footagepilot.recreate.check_sources',return_value={'needs_research':False}),patch('footagepilot.recreate.plan_visual',return_value={'manifest':str(root/'edit.json')}),patch('footagepilot.resolve.prepare',return_value={'job':str(root/'native/job.json'),'console':str(root/'native/console.lua')}),patch('footagepilot.recreate.render_edit') as edits:
                result=recreate(spec,root/'run',backend='resolve')
            self.assertFalse(result['passed']);self.assertEqual(result['status'],'awaiting-native-render');edits.assert_not_called()
            self.assertEqual(json.loads((root/'run/run.json').read_text())['backend'],'resolve')

    def test_unknown_backend_rejected_before_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaisesRegex(ValueError,'Unknown native editor'):recreate(root/'missing',root/'run',backend='unknown')
            self.assertFalse((root/'run').exists())

    def test_foreign_native_project_cannot_finish_run(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec=root/'spec.json';spec.write_text('{}');job=root/'job.json';job.write_text(json.dumps({'project_name':'Expected project'}))
            state={'backend':'resolve','status':'awaiting-native-render','passed':False,'spec_path':str(spec),'spec_sha256':hashlib.sha256(spec.read_bytes()).hexdigest(),'native_job':str(job),'native_job_sha256':hashlib.sha256(job.read_bytes()).hexdigest()}
            (root/'run.json').write_text(json.dumps(state));drp=root/'foreign.drp'
            with zipfile.ZipFile(drp,'w') as z:z.writestr('project.xml','<Name>Other project</Name>');z.writestr('SeqContainer/timeline.xml','<x/>')
            with patch('footagepilot.resolve.verify') as verifier:
                with self.assertRaisesRegex(ValueError,'different native project'):finish_resolve(root,root/'movie.mp4',drp)
                verifier.assert_not_called()
            self.assertFalse(json.loads((root/'run.json').read_text())['passed'])

    def test_modified_job_cannot_finish_run(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec=root/'spec.json';spec.write_text('{}');job=root/'job.json';job.write_text('{}')
            state={'backend':'resolve','status':'awaiting-native-render','spec_path':str(spec),'spec_sha256':hashlib.sha256(spec.read_bytes()).hexdigest(),'native_job':str(job),'native_job_sha256':'different'}
            (root/'run.json').write_text(json.dumps(state));drp=root/'project.drp';drp.write_bytes(b'not read')
            with self.assertRaisesRegex(ValueError,'Native job changed'):finish_resolve(root,root/'movie.mp4',drp)
