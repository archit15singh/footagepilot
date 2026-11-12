"""Evaluate actual native graphics exports against retained native failure controls.

Run from the repository: python3 -m evals.resolve_graphics JOB EXPORT
  --tiny-title FAILED_NATIVE.mp4 --missing-layers CUT_ONLY_NATIVE.mp4 --work NEW_DIR
Private source media and failure exports are supplied locally, never downloaded by this eval.
"""
import argparse
import json
from pathlib import Path
from footagepilot.__main__ import write
from footagepilot.resolve import verify, title_matches, visual_matches


def evaluate(job_path, export, tiny_title, missing_layers, work):
    if work.exists():raise ValueError('Use a fresh evaluation directory')
    work.mkdir(parents=True)
    job=json.loads(job_path.read_text())
    if not all(job.get(k) for k in ('titles','overlays','transitions')):raise ValueError('Evaluation requires titles, collage and a dissolve')
    positive=verify(job_path,export,work/'positive.json')
    negatives=[]
    for name,path,check,expected in [('tiny-title',tiny_title,title_matches,'too small or unreadable'),('missing-layers',missing_layers,visual_matches,'differs visually')]:
        try:check(job,path)
        except ValueError as error:
            if expected not in str(error):raise ValueError('Control failed for an unexpected reason: '+str(error)) from error
            negatives.append({'control':name,'rejected':True,'reason':str(error)})
        else:raise ValueError('Verifier accepted negative control: '+name)
    result={'passed':True,'positive':positive,'negative_controls':negatives,'scope':'Sampled composition and title contrast/size, not OCR, listening, native provenance or creative acceptance'}
    write(work/'results.json',result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('job',type=Path);p.add_argument('export',type=Path);p.add_argument('--tiny-title',type=Path,required=True);p.add_argument('--missing-layers',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
    print(json.dumps(evaluate(a.job,a.export,a.tiny_title,a.missing_layers,a.work),indent=2))
