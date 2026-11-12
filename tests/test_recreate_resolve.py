import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from footagepilot.recreate import recreate,finish_resolve

class ResolveRecreationTests(unittest.TestCase):
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
