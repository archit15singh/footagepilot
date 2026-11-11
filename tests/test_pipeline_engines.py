import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from spliceforge.pipeline import produce


class PipelineEngines(unittest.TestCase):
    def test_invalid_selection_does_not_mutate_project(self):
        for engines in [[],['bad'],['remotion','remotion']]:
            with self.assertRaises(ValueError):produce(Path('missing.json'),'Test',engines=engines)

    def test_selected_engine_outputs_and_final_mix_proof(self):
        # Control-flow regression; actual rendering is evaluated separately.
        for engines in [None,['remotion'],['hyperframes'],['hyperframes','remotion']]:
            with self.subTest(engines=engines),TemporaryDirectory() as tmp:
                root=Path(tmp);path=root/'project.json';path.write_text(json.dumps({'source':str(root/'source.mp4'),'keep':[[0,2]],'audio':{'music':str(root/'music.wav')}}))
                (root/'source.mp4').write_bytes(b'source');(root/'music.wav').write_bytes(b'music');seen=[]
                def render(p):
                    engine=json.loads(p.read_text())['renderer'];seen.append(engine)
                    (root/'output.mp4').write_bytes(engine.encode());(root/'verification.json').write_text('{}')
                def mix(video,output,settings,duration):
                    output.write_bytes(video.read_bytes()+b'mixed');return {'engine':video.stem.split('-')[0]}
                with patch('spliceforge.pipeline.align'),patch('spliceforge.pipeline.plan'),patch('spliceforge.pipeline.apply_plan'),patch('spliceforge.pipeline.render',side_effect=render),patch('spliceforge.pipeline.mix_audio',side_effect=mix),patch('spliceforge.pipeline.binary',return_value='ffmpeg'),patch('spliceforge.pipeline.run'),patch('spliceforge.pipeline.probe',return_value={'format':{'duration':'2'},'streams':[{'codec_type':'video'},{'codec_type':'audio'}]}):
                    state=produce(path,'Test',False,engines)
                expected=engines or ['remotion','hyperframes'];self.assertEqual(seen,expected)
                self.assertEqual(len(state['outputs']),2*len(expected));self.assertEqual(state['status'],'passed')
                proof=json.loads((root/'verification.json').read_text());self.assertEqual(proof['audio_mix']['engine'],expected[-1])
                self.assertEqual((root/'output.mp4').read_bytes(),expected[-1].encode()+b'mixed')
