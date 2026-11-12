import copy,json,tempfile,unittest
from pathlib import Path
from footagepilot.typography import apply_type,refine_typography

class TypographyTests(unittest.TestCase):
    def fixture(self,root):
        (root/'a.jpg').touch();(root/'music.wav').touch()
        spec={'native_backend':'resolve','assets':[{'id':'a','path':'a.jpg'}],'music':'music.wav','music_timing':{'bpm':120,'provenance':'authored'},'min_seconds':2,'max_seconds':2}
        plan={'title':'Old','shots':[{'asset_id':'a','beats':1,'fit':'fill','zoom':0}]*4,'panels':[]}
        words=['Small','days','big','memories']
        payload={'title_size':8,'title_bold':True,'title_font':'Helvetica Neue','title_color':'#FFFFFF','title_sequence':[{'text':w,'start_beat':i,'beats':1,'y':.3} for i,w in enumerate(words)]}
        manifest={'shots':[{'path':'original.mp4','duration':1,'focus_y':.8}],'plates':[{'path':'effect.mp4','start':.1,'duration':.2}],'music':'original.wav','titles':[{'text':'Old'}]}
        return spec,plan,words,payload,manifest

    def test_only_titles_change_and_original_input_stays_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec,plan,words,payload,manifest=self.fixture(root);before=copy.deepcopy(manifest)
            revised=apply_type(payload,plan,spec,root,manifest,words)
            self.assertEqual(manifest,before);self.assertEqual({k:v for k,v in revised.items() if k!='titles'},{k:v for k,v in before.items() if k!='titles'})
            self.assertEqual([t['text'] for t in revised['titles']],words);self.assertEqual([t['start'] for t in revised['titles']],[0,.5,1,1.5])

    def test_invented_reordered_words_merged_intervals_and_unknown_fields_reject(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec,plan,words,payload,manifest=self.fixture(root)
            for mutation in ('words','order','merge','field','size','font','colour'):
                bad=copy.deepcopy(payload)
                if mutation=='words':bad['title_sequence'][0]['text']='Copied creator phrase'
                if mutation=='order':bad['title_sequence'].reverse()
                if mutation=='merge':bad['title_sequence'][0]['beats']=2
                if mutation=='field':bad['shots']=[]
                if mutation=='size':bad['title_size']=72
                if mutation=='font':bad['title_font']='Uninstalled'
                if mutation=='colour':bad['title_color']='#FF0000'
                with self.assertRaises(ValueError):apply_type(bad,plan,spec,root,manifest,words)

    def test_stale_verified_inputs_stop_before_model_or_output(self):
        import hashlib
        from unittest.mock import patch
        for changed,message in (('movie.mp4','movie or edit'),('job.json','native job'),('visual-spec.json','specification'),('source.jpg','sources or prepared')):
            with self.subTest(changed=changed),tempfile.TemporaryDirectory() as td:
                root=Path(td);(root/'plan').mkdir();source=root/'source.jpg';source.write_bytes(b'source');movie=root/'movie.mp4';movie.write_bytes(b'movie')
                manifest=root/'edit.json';manifest.write_text(json.dumps({'shots':[{'path':'source.jpg','duration':1}]}));spec=root/'visual-spec.json';spec.write_text('{}')
                (root/'plan/plan.json').write_text(json.dumps({'input_hashes':{str(spec.resolve()):hashlib.sha256(spec.read_bytes()).hexdigest()}}))
                job=root/'job.json';job.write_text(json.dumps({'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'inputs':{str(source):hashlib.sha256(source.read_bytes()).hexdigest()},'prepared_hashes':{}}))
                (root/'native-verification.json').write_text(json.dumps({'technical_pass':True,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest()}))
                (root/'run.json').write_text(json.dumps({'backend':'resolve','status':'verified-export','native_manifest':str(manifest),'native_job':str(job),'native_job_sha256':hashlib.sha256(job.read_bytes()).hexdigest(),'output':str(movie)}))
                target=root/changed
                if changed=='job.json':data=json.loads(target.read_text());data['extra']='changed';target.write_text(json.dumps(data))
                elif changed=='visual-spec.json':target.write_text('{"changed":true}')
                else:target.write_bytes(b'replaced')
                with patch('footagepilot.typography.subprocess.run') as model:
                    with self.assertRaisesRegex(ValueError,message):refine_typography(root,['Small'],root/'review')
                    model.assert_not_called()
                self.assertFalse((root/'review').exists())

    def test_unverified_run_and_bad_words_cannot_start_review(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'run.json').write_text('{"backend":"resolve","status":"awaiting-native-render"}')
            for words in ([],[''],['x'*29],['a\nb'],['a']*9):
                with self.assertRaises(ValueError):refine_typography(root,words,root/'review')
            with self.assertRaisesRegex(ValueError,'verified native'):refine_typography(root,['Small'],root/'review')
            self.assertFalse((root/'review').exists())
