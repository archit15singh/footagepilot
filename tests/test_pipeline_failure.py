import json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from footagepilot.pipeline import produce


class PipelineFailure(unittest.TestCase):
    def test_audio_settings_survive_renderer_or_mixer_failure(self):
        for fail_at in ['remotion','hyperframes','mix']:
            for audio in ([{'music':'preserve-this.wav'},{}] if fail_at!='mix' else [{'music':'preserve-this.wav'}]):
                with self.subTest(fail_at=fail_at,audio=audio),TemporaryDirectory() as tmp:
                    root=Path(tmp);path=root/'project.json';original={'source':'source.mp4','keep':[[0,2]],'audio':audio};path.write_text(json.dumps(original))
                    def render(p):
                        engine=json.loads(p.read_text())['renderer']
                        if engine==fail_at:raise ValueError('Injected renderer failure')
                        (root/'output.mp4').write_bytes(b'video');(root/'verification.json').write_text('{}')
                    def mix(video,output,settings,duration):
                        if fail_at=='mix':raise ValueError('Injected mix failure')
                        output.write_bytes(b'mixed');return {}
                    with patch('footagepilot.pipeline.align'),patch('footagepilot.pipeline.plan'),patch('footagepilot.pipeline.apply_plan'),patch('footagepilot.pipeline.render',side_effect=render),patch('footagepilot.pipeline.mix_audio',side_effect=mix),patch('footagepilot.pipeline.binary',return_value='ffmpeg'),patch('footagepilot.pipeline.run'),patch('footagepilot.pipeline.probe',return_value={'format':{'duration':'2'},'streams':[]}):
                        with self.assertRaisesRegex(ValueError,'Injected'):produce(path,'Test',False)
                    current=json.loads(path.read_text());self.assertIn('audio',current);self.assertEqual(current['audio'],audio)
                    self.assertEqual(current['source'],original['source']);self.assertEqual(current['keep'],original['keep'])
                    state=json.loads((root/'pipeline-run.json').read_text());self.assertEqual(state['status'],'failed')
                    self.assertEqual(state['stages'][-1]['status'],'failed')
