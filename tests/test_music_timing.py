import hashlib,json,tempfile,unittest
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
from unittest.mock import patch
from footagepilot.music_timing import validate_timing,position,span,marker_times
from footagepilot.visual import compile_plan
from footagepilot.resolve import prepare


class MusicTimingTests(unittest.TestCase):
    def test_cue_spans_do_not_lose_half_frame_boundaries(self):
        timing={'cues':[0,.91,1.32,1.76,2.62,3.05,3.48,4.33,4.77,5.2]}
        elapsed=Decimal(0);frames=[]
        for start,length in [(0,2),(2,3),(5,4)]:
            elapsed+=Decimal(str(span(timing,start,length)))
            frames.append(int((elapsed*30).quantize(Decimal(1),rounding=ROUND_HALF_UP)))
        self.assertEqual(frames,[40,92,156])

    def cues(self,path):return {'mode':'onset_candidates','cues':[0,.37,1.1,2.4,4],'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'provenance':'measured transients, not beats'}

    def test_nonuniform_coordinates_and_music_binding(self):
        with tempfile.TemporaryDirectory() as td:
            music=Path(td)/'track.wav';music.write_bytes(b'first');timing=self.cues(music)
            validate_timing(timing,music)
            self.assertAlmostEqual(span(timing,1,2),2.03)
            self.assertEqual(marker_times(timing,4),[0,.37,1.1,2.4])
            for index in (.5,5,-1,float('nan')):
                with self.assertRaises(ValueError):position(timing,index)
            music.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'changed music'):validate_timing(timing,music)
            for cues in ([0,.01,1],[0,1,.5],[0,float('nan'),1]):
                with self.assertRaises(ValueError):validate_timing({**timing,'cues':cues})
            with self.assertRaises(ValueError):validate_timing({**timing,'bpm':120})

    def test_compiler_maps_shots_panels_titles_to_uneven_intervals(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.jpg').touch();music=root/'track.wav';music.touch()
            spec={'native_backend':'resolve','assets':[{'id':'a','path':'a.jpg'}],'music':'track.wav','music_timing':self.cues(music),'min_seconds':4,'max_seconds':4}
            plan={'title':'A day','shots':[{'asset_id':'a','beats':2,'fit':'fill','zoom':0}]*2,'panels':[{'asset_id':'a','start_beat':1,'beats':2,'x':.5,'y':.5,'width':.3,'height':.3}],'title_start_beat':1,'title_beats':2,'backgrounds':[{'start_beat':1,'beats':2}]}
            edit=compile_plan(plan,spec,root)
            self.assertEqual([s['duration'] for s in edit['shots']],[1.1,2.9])
            self.assertAlmostEqual(edit['titles'][0]['start'],.37)
            self.assertAlmostEqual(edit['titles'][0]['duration'],2.03)
            self.assertEqual(edit['layout_backgrounds'][0]['start'],.37)
            self.assertAlmostEqual(edit['overlays'][0]['duration'],2.03)
            with self.assertRaisesRegex(ValueError,'available audio cues'):compile_plan({**plan,'shots':[{**plan['shots'][0],'beats':8}]*2},spec,root)
            with self.assertRaisesRegex(ValueError,'requires Resolve'):compile_plan(plan,{**spec,'native_backend':'edits'},root)

    def test_native_marker_rounding_keeps_endpoint_outside_grid(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.jpg').write_bytes(b'input');(root/'track.wav').touch();timing=self.cues(root/'track.wav');timing['cues'][-1]=4.01
            manifest=root/'edit.json';manifest.write_text(json.dumps({'shots':[{'path':'a.jpg','duration':4.01}],'music':'track.wav','music_timing':timing}))
            def fake_run(cmd):Path(cmd[-1]).write_bytes(b'prepared')
            with patch('footagepilot.learning.check_sources',return_value={'needs_research':False}),patch('footagepilot.resolve.probe',return_value={'streams':[{'codec_type':'video'}],'format':{'duration':5}}),patch('footagepilot.resolve.run',side_effect=fake_run),patch('footagepilot.resolve.binary',return_value='ffmpeg'):
                prepare(manifest,root/'job')
            job=json.loads((root/'job/job.json').read_text());self.assertEqual(job['beats'],[0,11,33,72]);self.assertEqual(job['timing_mode'],'onset_candidates');self.assertIn('not verified beats',job['timing_label'])
