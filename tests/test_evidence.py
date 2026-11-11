import json
from pathlib import Path
import tempfile
import unittest
from spliceforge.evidence import input_revision,file_revision,current_verification

class EvidenceFreshness(unittest.TestCase):
    def test_changed_project_transcript_or_output_invalidates_proof(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'source.mp4';source.write_bytes(b'source')
            project=root/'project.json';item={'source':str(source),'keep':[[0,1]]};project.write_text(json.dumps(item))
            output=root/'output.mp4';output.write_bytes(b'output')
            def record():
                (root/'verification.json').write_text(json.dumps({'input_revision':input_revision(project),'output_revision':file_revision(output)}))
            record();self.assertIsNotNone(current_verification(project))
            item['keep']=[[0,.5]];project.write_text(json.dumps(item));self.assertIsNone(current_verification(project))
            record();(root/'transcript.json').write_text('{}');self.assertIsNone(current_verification(project))
            record();output.write_bytes(b'changed output');self.assertIsNone(current_verification(project))
