import hashlib,json,tempfile,unittest
from pathlib import Path
from footagepilot.reference_review import validate_review,iteration_notes


class ReferenceReviewTests(unittest.TestCase):
    def finding(self):return {'dimension':'layout','confidence':'visible','priority':1,'reference_ids':['r'],'candidate_ids':['c'],'observation':'Reference tiles fill upper row; candidate centers them.','revision':'Move the row upward and add a lower tile.','uncertainty':'Sampled frames do not establish every arrival.'}

    def test_citations_and_temporal_labels_cannot_be_promoted(self):
        validate_review({'summary':'No grounded revision found','findings':[]},['r'],['c'])
        row=self.finding();validate_review({'summary':'Layout differs','findings':[row]},['r'],['c'])
        for bad in ({**row,'reference_ids':['unknown']},{**row,'candidate_ids':[]},{**row,'dimension':'pacing'},{**row,'priority':0}):
            with self.assertRaises(ValueError):validate_review({'summary':'Review','findings':[bad]},['r'],['c'])

    def test_iteration_is_unreviewed_and_bound_to_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);ref=root/'ref.json';ref.write_text('{}');candidate=root/'clip.mp4';candidate.write_bytes(b'video');frame=root/'frame.jpg';frame.write_bytes(b'image')
            r={'kind':'model-reference-review','creative_acceptance':'unreviewed','summary':'Consider row placement','findings':[self.finding()],'reference_frames':[{'id':'r'}],'candidate_frames':[{'id':'c'}],'candidate':str(candidate),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'reference_analysis_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'input_hashes':{str(frame):hashlib.sha256(frame.read_bytes()).hexdigest()}}
            path=root/'review.json';path.write_text(json.dumps(r));spec={'reference':'ref.json','model_reviews':['review.json']}
            notes,files=iteration_notes(spec,root);self.assertIn('not human preferences',notes[0]['source']);self.assertIn(candidate,files)
            frame.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'evidence changed'):iteration_notes(spec,root)
            path.write_text(json.dumps({**r,'creative_acceptance':'accepted'}))
            with self.assertRaisesRegex(ValueError,'human acceptance'):iteration_notes(spec,root)
