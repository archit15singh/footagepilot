import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from footagepilot.visual import compile_plan,schema,plate_catalog
from footagepilot.reference_evidence import validate_observations


class PlannedPlateTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.root=Path(self.directory.name)
        for name in ('a.jpg','plate.mp4','score.wav'):(self.root/name).touch()
        self.spec={'native_backend':'resolve','assets':[{'id':'a','path':'a.jpg'}],
                   'plate_assets':[{'id':'light','path':'plate.mp4'}],
                   'music':'score.wav','music_timing':{'bpm':120,'offset':0,'provenance':'authored'},
                   'min_seconds':2,'max_seconds':8}
        self.plan={'title':'Travel','shots':[{'asset_id':'a','beats':4,'fit':'fill','zoom':0}]*2,
                   'plates':[{'asset_id':'light','after_shot':0,'pre_frames':6,'post_frames':12,
                              'source_start':.1,'opacity':.6,'reference_ids':['ref-1'],'reason':'One restrained light accent'}]}
        mocked=patch('footagepilot.visual.probe',return_value={'streams':[{'codec_type':'video','duration':'.8'}]})
        mocked.start();self.addCleanup(mocked.stop)

    def test_plate_anchor_preserves_main_edit_and_exact_frame_span(self):
        before=compile_plan({**self.plan,'plates':[]},self.spec,self.root)
        after=compile_plan(self.plan,self.spec,self.root)
        plate=after.pop('plates')[0]
        self.assertEqual(before,after)
        self.assertEqual((plate['start'],plate['duration'],plate['opacity']),(54/30,18/30,.6))
        self.assertEqual(plate['path'],str((self.root/'plate.mp4').resolve()))
        self.assertNotIn('plates',before)

    def test_plate_choice_rejects_unknown_boundary_asset_ranges_and_duplicates(self):
        for change in ({'asset_id':'a'},{'after_shot':1},{'after_shot':False},{'pre_frames':0},
                       {'pre_frames':6.5},{'post_frames':31},{'source_start':.3},
                       {'source_start':float('nan')},{'opacity':0},{'opacity':True}):
            with self.subTest(change=change):
                plan=copy.deepcopy(self.plan);plan['plates'][0].update(change)
                with self.assertRaises(ValueError):compile_plan(plan,self.spec,self.root)
        plan=copy.deepcopy(self.plan);plan['plates']*=2
        with self.assertRaisesRegex(ValueError,'unique adjacent'):compile_plan(plan,self.spec,self.root)
        with self.assertRaisesRegex(ValueError,'explicit list'):compile_plan({k:v for k,v in self.plan.items() if k!='plates'},self.spec,self.root)
        with self.assertRaisesRegex(ValueError,'Unknown planned plate'):compile_plan(self.plan,{**self.spec,'plate_assets':[]},self.root)

    def test_cut_anchor_uses_cumulative_half_up_rounding(self):
        spec={**self.spec,'music_timing':{'bpm':80,'offset':0,'provenance':'authored'}}
        plan=copy.deepcopy(self.plan);plan['shots'][0]={**plan['shots'][0],'beats':1}
        result=compile_plan(plan,spec,self.root)
        self.assertAlmostEqual(result['plates'][0]['start'],17/30)  # .75s is frame23, not22.

    def test_subtle_missing_plate_rejected_in_active_region(self):
        from footagepilot.resolve import plate_matches
        job={'fps':30,'shots':[{'path':'base','start':0,'frames':30}],
             'plates':[{'path':'plate','start':0,'frames':30,'blend':'screen','opacity':1}]}
        def frame(path,number,fps,width=64,height=64):
            values={'base':[.2,.4,.6],'plate':[.1,.1,.1],
                    'native':[.28,.46,.64],'missing':[.2,.4,.6]}[path]
            return values*(width*height)
        with patch('footagepilot.resolve.sample_frame',side_effect=frame):
            self.assertEqual(len(plate_matches(job,'native')),3)
            with self.assertRaisesRegex(ValueError,'active pixels'):plate_matches(job,'missing')
            job['plates'][0]['opacity']=0
            with self.assertRaisesRegex(ValueError,'insufficient distinguishable'):plate_matches(job,'native')

    def test_catalog_limits_and_backend_reject_before_model_usage(self):
        for rows in (None,[{}],[{'id':'x','path':'p'}]*2,[{'id':str(n),'path':'p'} for n in range(9)]):
            with self.subTest(rows=rows),self.assertRaises(ValueError):plate_catalog({**self.spec,'plate_assets':rows})
        with self.assertRaisesRegex(ValueError,'requires Resolve'):plate_catalog({**self.spec,'native_backend':'edits'})

    def test_schema_keeps_plate_ids_out_of_main_shots(self):
        contract=schema(['a'],video_ranges=True,reference_ids=['ref-1'],plate_ids=['light'])
        self.assertEqual(contract['properties']['plates']['items']['properties']['asset_id']['enum'],['light'])
        self.assertEqual(contract['properties']['shots']['items']['properties']['asset_id']['enum'],['a'])
        self.assertIn('plates',contract['required'])
        self.assertNotIn('plates',schema(['a'])['properties'])

    def test_plate_evidence_cannot_invent_citations_or_visible_motion(self):
        payload={'reference_techniques':[{'technique':'motion_plate','frame_ids':['ref-1'],
                 'confidence':'visible','adaptation':'Possibly a moving light layer'}], 'plates':self.plan['plates']}
        with self.assertRaisesRegex(ValueError,'inferred label'):validate_observations(payload,[{'id':'ref-1'}])
        payload['reference_techniques'][0]['confidence']='inferred'
        self.assertEqual(validate_observations(payload,[{'id':'ref-1'}])['observation_count'],1)
        payload['plates'][0]['reference_ids']=['invented']
        with self.assertRaisesRegex(ValueError,'unknown reference'):validate_observations(payload,[{'id':'ref-1'}])


if __name__=='__main__':unittest.main()
