import hashlib,json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
from spliceforge.planner import plan


class PlanningSnapshot(unittest.TestCase):
    def run_model(self,mutation=None):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source.mp4';source.write_bytes(b'original source')
            project=root/'project.json';project.write_text(json.dumps({'source':str(source),'keep':[[0,10]]}))
            words=root/'words.json';words.write_text(json.dumps({'source':str(source),'words':[{'text':'A','start':1,'end':2},{'text':'sentence.','start':2,'end':3}]}))
            original=words.read_bytes()
            def model(command,**kwargs):
                output=Path(command[command.index('-o')+1]);output.write_text(json.dumps({'title':'Test','rationale':'Test','ranges':[{'first_word':0,'last_word':1,'reason':'Test'}]}))
                if mutation=='words':words.write_text(words.read_text().replace('sentence.','different.'))
                elif mutation=='project':project.write_text(project.read_text()+'\n')
                elif mutation=='source':source.write_bytes(b'changed source content')
                return SimpleNamespace(returncode=0,stderr='')
            with patch('spliceforge.__main__.probe',return_value={'format':{'duration':'10'}}),patch('spliceforge.planner.subprocess.run',side_effect=model):
                if mutation:
                    with self.assertRaisesRegex(ValueError,'inputs changed'):plan(project,'Keep the sentence')
                    self.assertFalse((root/'plan.json').exists())
                else:
                    result=plan(project,'Keep the sentence');self.assertEqual(result['words_sha256'],hashlib.sha256(original).hexdigest())

    def test_changed_inputs_during_model_call_are_rejected(self):
        for mutation in ['words','project','source']:
            with self.subTest(mutation=mutation):self.run_model(mutation)

    def test_unchanged_snapshot_is_accepted(self):
        self.run_model()
