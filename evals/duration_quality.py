"""Budget rejection sensitivity on real transcript word selections."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from spliceforge.planner import planned_ranges,validate_plan
from spliceforge.duration import require_duration


def evaluate():
    words=json.loads((Path(__file__).resolve().parents[1]/'evals/fixtures/weekly-address-words.json').read_text())['words'];budget={'min_seconds':20,'max_seconds':35}
    cases={'published':([(2,35),(57,100)],True),'too_short':([(2,13)],False),'too_long':([(0,130)],False),'padding_over_budget':([(2,35),(57,100)],False)}
    rows=[]
    for name,(selections,valid) in cases.items():
        plan={'title':'Test','rationale':'Test','ranges':[{'first_word':a,'last_word':b,'reason':'Evaluation'} for a,b in selections]}
        validate_plan(plan,words) # Previous structural-only gate accepts every case.
        seconds=sum(b-a for a,b in planned_ranges(plan,words,38.282))
        target=budget if name!='padding_over_budget' else {'min_seconds':20,'max_seconds':21.25}
        try:require_duration(seconds,target);accepted=True
        except ValueError:accepted=False
        assert accepted==valid,(name,seconds)
        rows.append({'case':name,'seconds':seconds,'budget':target,'baseline_accepts':True,'candidate_accepts':accepted,'should_accept':valid})
    return {'gate':'passed','cases':rows,'baseline_invalid_accepted':3,'candidate_invalid_accepted':0,'scope':'Explicit duration contract, not semantic or storytelling quality'}

if __name__=='__main__':print(json.dumps(evaluate(),indent=2))
