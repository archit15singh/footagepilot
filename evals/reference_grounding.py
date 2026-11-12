"""Actual planner evidence ledger plus fabricated-citation/temporal-overclaim controls."""
import argparse,copy,json
from pathlib import Path
from footagepilot.reference_evidence import validate_observations
from footagepilot.__main__ import write


def evaluate(plan_path,output):
    if output.exists():raise ValueError('Use a fresh result file')
    plan=json.loads(plan_path.read_text());frames=plan['reference_evidence_frames'];positive=validate_observations(plan,frames);negatives=[]
    unknown=copy.deepcopy(plan);unknown['reference_techniques'][0]['frame_ids']=['fabricated-frame']
    overclaim=copy.deepcopy(plan);overclaim['reference_techniques'][0].update(technique='camera_motion',confidence='visible')
    for name,payload,expected in [('fabricated-frame',unknown,'unknown frames'),('motion-as-visible',overclaim,'inferred label')]:
        try:validate_observations(payload,frames)
        except ValueError as error:
            if expected not in str(error):raise
            negatives.append({'control':name,'rejected':True,'reason':str(error)})
        else:raise ValueError('Evidence gate accepted '+name)
    result={'passed':True,'positive':positive,'negative_controls':negatives,'observed_techniques':[{'technique':r['technique'],'confidence':r['confidence'],'cited_frame_count':len(r['frame_ids'])} for r in plan['reference_techniques']],'shots_with_citations':sum(bool(r['reference_ids']) for r in plan['shots']),'limits':['Model classifications are claims, not validated semantic truth.','Cited frames remain sparse; no continuous motion, listening or creative preference verdict.']};write(output,result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(evaluate(a.plan,a.output),indent=2))
