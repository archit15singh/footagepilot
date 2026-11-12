"""Fetch a reviewed public-domain effect; preserve source, license evidence and recipe."""
import hashlib,re
from datetime import date
from fractions import Fraction
from html.parser import HTMLParser
from urllib.request import urlopen
from .__main__ import binary,probe,run,write

PLATES={'marburg-glass':{
    'url':'https://www.mathematik.uni-marburg.de/~thormae/misc/breaking_glass_overlay_h264.mp4',
    'source_page':'https://www.uni-marburg.de/en/fb12/research-groups/grafikmultimedia/research/studio',
    'credit':'OpenStudioMarburg, Philipps-Universität Marburg',
    'license':'CC0-1.0','reviewed_at':'2026-11-12','max_age_days':30,
    'bytes':8769929,'sha256':'8014be86ef8e29c92194b086974cd6a32444b8165fbc6adfb8f34b9e7755f247',
    'recipe':{'source_start':0,'duration':1,'crop':[480,120,640,360],'width':1920,'height':1080,'fps':30,
              'fade_in':[.12,.12],'fade_out':[.6,.2]},
    'note':'CC0 real breaking-glass footage, cropped from a 640x360 source region and upscaled to1920x1080. First impact/bright shards near0.4–0.6s; fade clears by0.8s. Screen overlay, not refraction of the underlying footage.'}}


class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,data):self.parts.append(data)


def license_evidence(body):
    parser=Text();parser.feed(body.decode('utf-8'))
    text=re.sub(r'\s+',' ',' '.join(parser.parts));start=text.find('Breaking Glass Overlay');end=text.find('Long Exposure Photography',start)
    section=text[start:end] if start>=0 and end>start else ''
    if 'Public Domain, Creative Commons CC0' not in section or 'breaking_glass_overlay_h264.mp4' not in body.decode('utf-8'):raise ValueError('Glass source/license evidence changed; review the publisher page before updating the catalog')
    return section.strip()


def download(url,target,maximum,expected=None):
    digest=hashlib.sha256();count=0
    with urlopen(url,timeout=30) as response,target.open('xb') as stream:
        while True:
            chunk=response.read(min(1024*1024,maximum-count+1))
            if not chunk:break
            count+=len(chunk)
            if count>maximum:raise ValueError('Plate download exceeds reviewed size bound')
            digest.update(chunk);stream.write(chunk)
    if expected and (count!=expected['bytes'] or digest.hexdigest()!=expected['sha256']):raise ValueError('Plate download differs from reviewed bytes/hash; do not use until researched')
    return {'bytes':count,'sha256':digest.hexdigest()}


def fetch_plate(name,output):
    if name not in PLATES:raise ValueError('Unknown reviewed plate')
    entry=PLATES[name]
    age=(date.today()-date.fromisoformat(entry['reviewed_at'])).days
    if not 0<=age<=entry['max_age_days']:raise ValueError('Plate source review is stale; re-research its license, URL and bytes before updating the catalog')
    if output.exists():raise ValueError('Use a fresh effect asset directory')
    output.mkdir(parents=True);record={'status':'fetching','asset_id':name,**entry}
    try:
        page=output/'license-source.html';evidence=download(entry['source_page'],page,2*1024**2)
        section=license_evidence(page.read_bytes());(output/'license-excerpt.txt').write_text(section+'\n')
        record['license_evidence']={**evidence,'observed_on':date.today().isoformat(),'section':section}
        source=output/'original.mp4';record['download']=download(entry['url'],source,entry['bytes'],entry)
        meta=probe(source);video=next((s for s in meta['streams'] if s['codec_type']=='video'),None)
        if not video or (video['width'],video['height'])!=(1280,720):raise ValueError('Reviewed plate geometry changed')
        run([binary('ffmpeg'),'-v','error','-i',source,'-map','0:v:0','-f','null','-'])
        recipe=entry['recipe'];x,y,w,h=recipe['crop'];fi,fd=recipe['fade_in'];fo,od=recipe['fade_out']
        filt=f"crop={w}:{h}:{x}:{y},scale={recipe['width']}:{recipe['height']},setsar=1,fade=t=in:st={fi}:d={fd},fade=t=out:st={fo}:d={od}"
        asset=output/'glass-impact.mp4'
        run([binary('ffmpeg'),'-v','error','-n','-ss',recipe['source_start'],'-i',source,'-an','-vf',filt,'-r',recipe['fps'],'-frames:v',round(recipe['duration']*recipe['fps']),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p',asset])
        run([binary('ffmpeg'),'-v','error','-i',asset,'-map','0:v:0','-f','null','-'])
        derived=probe(asset);stream=next((s for s in derived['streams'] if s['codec_type']=='video'),None)
        if not stream or (stream['width'],stream['height'])!=(recipe['width'],recipe['height']) or Fraction(stream['avg_frame_rate'])!=recipe['fps'] or abs(float(stream['duration'])-recipe['duration'])>1/recipe['fps']:raise ValueError('Derived effect geometry, FPS or duration differs from recipe')
        record['derived_media']={'width':stream['width'],'height':stream['height'],'fps':str(stream['avg_frame_rate']),'duration':stream['duration']}
        if hashlib.sha256(source.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Original effect changed during preparation')
        record.update(status='verified-local-asset',source_decode='passed',derived_decode='passed',derived_sha256=hashlib.sha256(asset.read_bytes()).hexdigest())
        catalog=output/'plate-assets.json';write(catalog,{'plate_assets':[{'id':name,'path':str(asset.resolve()),'note':entry['note']}]})
        write(output/'provenance.json',record)
        return {'status':record['status'],'plate_catalog':str(catalog),'asset':str(asset),'license':entry['license'],'credit':entry['credit'],'source_sha256':entry['sha256'],'derived_sha256':record['derived_sha256']}
    except Exception as error:
        record.update(status='failed',error=str(error));write(output/'provenance.json',record);raise
