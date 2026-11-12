"""Repeated real-panel decoding regression; needs an actual prepared Resolve job."""
import argparse,hashlib,json
from pathlib import Path
from footagepilot.__main__ import write
from footagepilot.layout import rectangle
from footagepilot.resolve import sample_frame


def evaluate(job_path,output):
    if output.exists():raise ValueError('Use a new sampling evaluation directory')
    job=json.loads(job_path.read_text());panels=job.get('overlays',[])
    if not panels:raise ValueError('Use a job with actual prepared panel clips')
    output.mkdir(parents=True);rows=[]
    try:
        for index,panel in enumerate(panels):
            source=Path(panel['path']);digest=hashlib.sha256(source.read_bytes()).hexdigest()
            left,top,right,bottom=rectangle(panel)
            for resolution in (64,256):
                width=round(right*resolution)-round(left*resolution);height=round(bottom*resolution)-round(top*resolution)
                for number in sorted({0,panel['frames']//2,panel['frames']-1}):
                    hashes=[]
                    for repeat in range(3):
                        pixels=sample_frame(source,number,job['fps'],width,height)
                        hashes.append(hashlib.sha256(bytes(round(p*255) for p in pixels)).hexdigest())
                    rows.append({'panel':index+1,'frame':number,'size':[width,height],'repeat_hashes':hashes})
                    write(output/'samples.json',rows)
                    if len(set(hashes))!=1:raise ValueError('Repeated QA frame samples differ')
            if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:raise ValueError('Prepared source changed during sampling')
        result={'passed':True,'sample_calls':sum(len(r['repeat_hashes']) for r in rows),'frame_size_groups':len(rows),'scope':'Repeated exact pixels for supplied prepared clips; not a universal decoder guarantee or aesthetic score'}
        write(output/'results.json',result);return result
    except Exception as error:write(output/'failure.json',{'error':str(error),'completed_groups':len(rows)});raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('job',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(evaluate(a.job,a.output),indent=2))
