import tempfile,unittest
from pathlib import Path
from footagepilot.reference_evidence import select_frames,validate_observations


class ReferenceEvidenceTests(unittest.TestCase):
    def test_selection_is_bounded_temporal_and_includes_change_neighbours(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'frames').mkdir();frames=[]
            for i in range(101):
                name=f'frames/{i:04d}.jpg';(root/name).touch();frames.append({'time':i/10,'file':name})
            chosen=select_frames({'duration':10,'frames':frames,'scene_changes':[2,5,8]},root)
            self.assertLessEqual(len(chosen),18);self.assertEqual([r['time'] for r in chosen],sorted(r['time'] for r in chosen))
            self.assertTrue({4.9,5.,5.1}.issubset({r['time'] for r in chosen}))
            focused=select_frames({'duration':10,'frames':frames,'scene_changes':[2,5,8]},root,times=[1.0])
            self.assertIn(1.0,[r['time'] for r in focused]);self.assertLessEqual(len(focused),20)
            for times in ([11],[float('nan')],[1,2,3]):
                with self.assertRaisesRegex(ValueError,'focus times'):select_frames({'duration':10,'frames':frames},root,times=times)
            with self.assertRaisesRegex(ValueError,'Invalid reference frame'):select_frames({'duration':10,'frames':[{'time':0,'file':'../secret.jpg'}]},root)

    def test_unknown_citations_and_temporal_overclaims_rejected(self):
        frames=[{'id':'ref-0000','time':0}]
        row={'technique':'camera_motion','frame_ids':['ref-0000'],'confidence':'visible','adaptation':'Possible camera movement; needs continuous review'}
        payload={'reference_techniques':[row],'shots':[{'reference_ids':['ref-0000']}],'panels':[]}
        with self.assertRaisesRegex(ValueError,'inferred label'):validate_observations(payload,frames)
        row['confidence']='inferred';self.assertEqual(validate_observations(payload,frames)['observation_count'],1)
        payload['shots'][0]['reference_ids']=['invented']
        with self.assertRaisesRegex(ValueError,'unknown reference'):validate_observations(payload,frames)
        payload['shots'][0]['reference_ids']=[];row['frame_ids']=['invented']
        with self.assertRaisesRegex(ValueError,'unknown frames'):validate_observations(payload,frames)
