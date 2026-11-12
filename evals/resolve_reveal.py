"""Actual native reveal: correspondence, timing and wrong-recipe negative controls."""
import argparse
import copy
import json
from pathlib import Path
from footagepilot.__main__ import write
from footagepilot.resolve import verify,visual_matches


def evaluate(job_path,media,baseline,work):
    if work.exists():raise ValueError('Use a fresh evaluation directory')
    work.mkdir(parents=True);job=json.loads(job_path.read_text())
    if not any(r.get('filter')=='transition_wipe_left' for r in job.get('transitions',[])):raise ValueError('Supply a native wipe-left job')
    positive=verify(job_path,media,work/'positive.json');wrong=copy.deepcopy(job)
    for row in wrong['transitions']:row['filter']='transition_dissolve'
    negatives=[]
    for name,expected,export in [('dissolve-hypothesis',wrong,media),('earlier-dissolve-export',job,baseline)]:
        try:visual_matches(expected,export)
        except ValueError as error:
            if 'differs visually' not in str(error):raise
            negatives.append({'control':name,'rejected':True,'reason':str(error)})
        else:raise ValueError('Negative accepted: '+name)
    result={'passed':True,'positive':positive,'negative_controls':negatives,'scope':'Spatial reveal and authored grid correspondence, not taste or inferred beats'}
    write(work/'results.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('job',type=Path);p.add_argument('media',type=Path);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
    print(json.dumps(evaluate(a.job,a.media,a.baseline,a.work),indent=2))
