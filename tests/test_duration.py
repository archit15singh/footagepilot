import json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from footagepilot.duration import validate_budget
from footagepilot.planner import apply_plan
from footagepilot.__main__ import render
from evals.duration_quality import evaluate


class DurationBudget(unittest.TestCase):
    def test_real_selection_budget_gate(self):
        self.assertEqual(evaluate()['gate'],'passed')

    def test_invalid_budgets(self):
        for budget in [{},[],{'min_seconds':True,'max_seconds':20},{'min_seconds':-1,'max_seconds':20},{'min_seconds':20,'max_seconds':20},{'min_seconds':0,'max_seconds':float('inf')}]:
            with self.subTest(budget=budget),self.assertRaises(ValueError):validate_budget(budget)

    def test_over_budget_never_renders_or_mutates_project(self):
        import hashlib
        with TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'project.json';source=root/'source.mp4';source.touch()
            path.write_text(json.dumps({'source':str(source),'keep':[[0,10]],'duration_budget':{'min_seconds':0,'max_seconds':2}}));original=path.read_bytes()
            words={'source':str(source),'words':[{'text':'Sentence.','start':0,'end':5}]};raw=json.dumps(words).encode();(root/'words.json').write_bytes(raw)
            (root/'plan.json').write_text(json.dumps({'title':'Test','rationale':'Test','ranges':[{'first_word':0,'last_word':0,'reason':'Test'}],'words_sha256':hashlib.sha256(raw).hexdigest()}))
            with patch('footagepilot.__main__.probe',return_value={'format':{'duration':'10'}}),patch('footagepilot.__main__.run') as run:
                with self.assertRaisesRegex(ValueError,'outside budget'):apply_plan(path)
                self.assertEqual(path.read_bytes(),original)
                with self.assertRaisesRegex(ValueError,'outside budget'):render(path)
                run.assert_not_called()
