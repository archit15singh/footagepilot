import json
import array
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from footagepilot.resolve import lua,prepare,verify,similarity,audio_match,expected_frame,timing_evidence

class ResolveTests(unittest.TestCase):
    def setUp(self):
        gate=patch("footagepilot.learning.check_sources",return_value={"needs_research":False})
        gate.start();self.addCleanup(gate.stop)

    def test_correspondence_rejects_constant_slate_and_reversed_structure(self):
        source=[.05,.2,.4,.8,.6]
        self.assertAlmostEqual(similarity(source,source)[1],1)
        self.assertLess(similarity(source,[.5]*5)[1],.9)
        self.assertLess(similarity(source,list(reversed(source)))[1],.9)
        with self.assertRaises(ValueError):similarity([],[])

    def test_audio_correspondence_rejects_wrong_gain_despite_same_waveform(self):
        a=array.array('f',[.2*math.sin(i*.1) for i in range(1000)])
        b=array.array('f',[x*.01 for x in a])
        with patch('footagepilot.resolve.raw',side_effect=[a.tobytes(),b.tobytes()]),patch('footagepilot.resolve.binary',return_value='ffmpeg'):
            with self.assertRaisesRegex(ValueError,'waveform does not match'):audio_match(Path('a'),Path('b'))

    def test_wipe_reference_is_spatial_not_global_opacity(self):
        job={'fps':30,'shots':[{'path':'out','start':0,'frames':10},{'path':'in','start':10,'frames':10}],'transitions':[{'path':'reveal','start':7,'frames':3,'filter':'transition_wipe_left'}]}
        def frame(path,*args):return ([.8] if path=='reveal' else [.2])*48
        with patch('footagepilot.resolve.sample_frame',side_effect=frame):
            actual=expected_frame(job,8,4,4)
        for y in range(4):
            self.assertEqual(actual[y*12:(y+1)*12],[.8]*6+[.2]*6)

    def test_screen_compositor_preserves_black_and_uses_fractional_opacity(self):
        job={'fps':30,'shots':[{'path':'base','start':0,'frames':30}],
             'plates':[{'path':'plate','start':3,'frames':12,'blend':'screen','opacity':.5}]}
        def frame(path,*args):return ([0.,1.,.5] if path=='plate' else [.2,.4,.6])*4
        with patch('footagepilot.resolve.sample_frame',side_effect=frame):
            self.assertEqual(expected_frame(job,0,2,2),[.2,.4,.6]*4)
            actual=expected_frame(job,8,2,2)
        for a,b in zip(actual,[.2,.7,.7]*4):self.assertAlmostEqual(a,b)

    def test_color_gate_rejects_neutral_export_that_passes_general_correspondence(self):
        from footagepilot.color import apply_saturation, color_preset
        from footagepilot.resolve import visual_matches

        job={'fps':30,'shots':[{'path':'source','start':0,'frames':30}],
             'color_preset':color_preset({'color_preset':'soft-color-v1'})}
        neutral=[.28,.42,.57]*(64*64)
        graded=apply_saturation(neutral,.65)
        brighter_graded=[channel+.025 for channel in graded]
        with patch('footagepilot.resolve.sample_frame',side_effect=lambda path,*args: brighter_graded if path=='graded' else neutral):
            self.assertTrue(visual_matches(job,'neutral'))
            checks=[]
            visual_matches(job,'graded',checks)
            self.assertEqual(len(checks),3)
            with self.assertRaisesRegex(ValueError,'Color preset missing'):
                visual_matches(job,'neutral',[])

    def test_color_preset_rejects_hdr_before_running_ffmpeg(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'source.mp4').touch()
            manifest=root/'edit.json'
            manifest.write_text(json.dumps({'color_preset':'monochrome-v1','shots':[{'path':'source.mp4','duration':1}]}))
            with patch('footagepilot.resolve.probe',return_value={'streams':[{'codec_type':'video','color_transfer':'smpte2084'}]}):
                with self.assertRaisesRegex(ValueError,'requires SDR'):
                    prepare(manifest,root/'job')
            self.assertFalse((root/'job').exists())

    def test_panel_region_gate_includes_screen_plate_above_it(self):
        from footagepilot.resolve import visual_matches
        job={'fps':30,'shots':[{'path':'base','start':0,'frames':30}],
             'overlays':[{'path':'panel','start':0,'frames':30,'x':.5,'y':.5,'width':.5,'height':.5}],
             'plates':[{'path':'plate','start':0,'frames':30,'blend':'screen','opacity':1}]}
        def frame(path,number,fps,width=64,height=64):
            if path!='native':return [{'base':.2,'panel':.4,'plate':.5}[path]]*(width*height*3)
            return [(.7 if width//4<=x<width*3//4 and height//4<=y<height*3//4 else .6)
                    for y in range(height) for x in range(width) for _ in range(3)]
        with patch('footagepilot.resolve.sample_frame',side_effect=frame):
            self.assertTrue(visual_matches(job,'native'))

    def test_plate_validation_rejects_unknown_mode_transform_and_nan(self):
        from footagepilot.edits import validate_edit,render_edit
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.jpg').write_bytes(b'input')
            data={'shots':[{'path':'a.jpg','duration':1}],
                  'plates':[{'path':'a.jpg','start':0,'duration':.4,'opacity':.75}]}
            for change in ({'blend':'add'},{'x':.5},{'opacity':float('nan')},{'start':.9}):
                bad={**data,'plates':[{**data['plates'][0],**change}]}
                with self.assertRaises(ValueError):validate_edit(bad,root)
            manifest=root/'edit.json';manifest.write_text(json.dumps(data))
            with patch('footagepilot.edits.EditsClient') as client:
                with self.assertRaisesRegex(ValueError,'plates require Resolve'):render_edit(manifest,root/'out.mp4')
                client.assert_not_called()

    def test_timing_reports_off_grid_cut_without_inventing_a_beat(self):
        report=timing_evidence({'shots':[{'start':0},{'start':17}],'beats':[0,15,30],'transitions':[{'start':12,'frames':5,'after_shot':0,'filter':'transition_wipe_left'}],'timing_provenance':'authored'})
        self.assertEqual(report['cuts'][0]['offset_frames'],2)
        self.assertEqual(report['transitions'][0]['last_effect_frame'],16)
        self.assertEqual(report['transitions'][0]['cut_frame'],17)
        self.assertIsNone(timing_evidence({'shots':[{'start':0},{'start':17}]})['cuts'][0]['nearest_grid_frame'])

    def test_lua_strings_cannot_escape_data(self):
        value='x\"; os.execute(\"bad\"); --\n\\ café'
        encoded=lua(value)
        self.assertNotIn('"bad"',encoded)
        self.assertIn('\\034',encoded)
        self.assertIn('\\010',encoded)
        self.assertIn('\\195\\169',encoded)
        with self.assertRaises(ValueError):lua(float('nan'))

    def test_unsupported_edit_fails_before_media_preparation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.jpg').write_bytes(b'input')
            manifest=root/'edit.json'
            manifest.write_text(json.dumps({'shots':[{'path':'a.jpg','duration':1}], 'overlays':[{'path':'a.jpg','start':0,'duration':1,'x':.5,'y':.5,'scale':1}]*2}))
            with self.assertRaisesRegex(ValueError,'overlap'):prepare(manifest,root/'job')
            self.assertFalse((root/'job').exists())

    def test_relative_output_produces_portable_native_paths(self):
        import os
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.jpg').write_bytes(b'input')
            manifest=root/'edit.json';manifest.write_text(json.dumps({'shots':[{'path':'a.jpg','duration':1}]}))
            relative=Path(os.path.relpath(root/'job',Path.cwd()))
            def render(cmd):Path(cmd[-1]).write_bytes(b'prepared')
            with patch('footagepilot.resolve.probe',return_value={'streams':[{'codec_type':'video'}]}),patch('footagepilot.resolve.run',side_effect=render),patch('footagepilot.resolve.binary',return_value='ffmpeg'):
                result=prepare(manifest,relative,render=True)
            self.assertTrue(Path(result['job']).is_absolute())
            job=json.loads(Path(result['job']).read_text())
            self.assertTrue(all(Path(row['path']).is_absolute() for row in job['shots']))
            self.assertIn(str(root/'job'),Path(result['console']).read_text())

    def test_styled_job_keeps_native_features_and_single_line_console(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.jpg').write_bytes(b'input')
            manifest=root/'edit.json';manifest.write_text(json.dumps({'shots':[{'path':'a.jpg','duration':1}]*2,'titles':[{'text':'A -- title','start':0,'duration':1,'size':28,'color':'#25372F'}],'overlays':[{'path':'a.jpg','start':1,'duration':1,'x':x,'y':y,'scale':.5} for x in (.25,.75) for y in (.25,.75)],'plates':[{'path':'a.jpg','start':.1,'duration':.4,'opacity':.75}],'transitions':[{'after_shot':0,'filter':'transition_dissolve','duration':.1}]}))
            def fake_run(cmd):Path(cmd[-1]).write_bytes(b'prepared')
            with patch('footagepilot.resolve.probe',return_value={'streams':[{'codec_type':'video'}]}),patch('footagepilot.resolve.run',side_effect=fake_run),patch('footagepilot.resolve.binary',return_value='ffmpeg'):
                prepare(manifest,root/'job',render=True)
            job=json.loads((root/'job/job.json').read_text());script=(root/'job/console.lua').read_text()
            self.assertEqual((len(job['titles']),len(job['overlays']),len(job['transitions'])),(1,4,1))
            self.assertEqual(job['transitions'][0]['start'],27)
            self.assertEqual(job['plates'][0]['start'],3)
            self.assertEqual(job['plates'][0]['frames'],12)
            self.assertIn(job['plates'][0]['path'],job['prepared_hashes'])
            self.assertIn('CompositeMode=5',script)
            self.assertEqual(script.count('\n'),1);self.assertIn('A -- title',script);self.assertIn('TextPlus',script)

    def test_cumulative_frame_rounding_and_hashed_preparation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.jpg').write_bytes(b'input')
            manifest=root/'edit.json';manifest.write_text(json.dumps({'fps':30,'shots':[{'path':'a.jpg','duration':.15}]*3}))
            def fake_run(cmd):Path(cmd[-1]).write_bytes(b'prepared')
            with patch('footagepilot.resolve.probe',return_value={'streams':[{'codec_type':'video'}]}),patch('footagepilot.resolve.run',side_effect=fake_run),patch('footagepilot.resolve.binary',return_value='ffmpeg'):
                prepare(manifest,root/'job')
            job=json.loads((root/'job/job.json').read_text())
            self.assertEqual(sum(s['frames'] for s in job['shots']),round(.45*30))
            self.assertEqual(job['shots'][1]['start'],job['shots'][0]['frames'])
            self.assertEqual(job['status'],'prepared-not-executed')
            self.assertIn('FOOTAGEPILOT_FAILED',(root/'job/console.lua').read_text())
            (root/'a.jpg').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'inputs changed'):verify(root/'job/job.json',root/'missing.mp4',root/'verification.json')

if __name__=='__main__':unittest.main()
