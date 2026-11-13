import tempfile,unittest,json
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch
from footagepilot.visual import compile_plan,plan_visual,review_notes

class VisualTests(unittest.TestCase):
    def test_planner_retries_unknown_frame_once_and_keeps_rejected_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'frames').mkdir()
            for name in ('a.jpg','b.jpg','contact.jpg','score.wav','frames/0000.jpg'):
                (root/name).touch()
            (root/'analysis.json').write_text(json.dumps({
                'decode':'passed','duration':4,'scene_changes':[],
                'frames':[{'time':0,'file':'frames/0000.jpg'}],'audio':{'method':'fixture'},
            }))
            spec=root/'spec.json'
            spec.write_text(json.dumps({
                'reference':'analysis.json','assets':[{'id':'a','path':'a.jpg'},{'id':'b','path':'b.jpg'}],
                'music':'score.wav','music_timing':{'bpm':120,'offset':0,'provenance':'authored'},
                'min_seconds':2,'max_seconds':8,
            }))
            for always_invalid in (False, True):
                prompts=[]
                def codex(command, *, input, **kwargs):
                    prompts.append(input)
                    frame='ref-9999' if always_invalid or len(prompts)==1 else 'ref-0000'
                    payload={'title':'Travel','shots':[{'asset_id':asset,'beats':4,'fit':'fill','zoom':0,
                                                       'reference_ids':[]} for asset in ('a','b')],
                             'reference_techniques':[{'technique':'full_frame','frame_ids':[frame],
                                                      'confidence':'visible','adaptation':'Full frame'}]}
                    Path(command[command.index('-o')+1]).write_text(json.dumps(payload))
                    return CompletedProcess(command,0,'','planner output')
                output=root/f'run-{always_invalid}'
                with (
                    patch('footagepilot.visual.asset_media',return_value={'kind':'still'}),
                    patch('footagepilot.visual.binary',return_value='ffmpeg'),
                    patch('footagepilot.visual.run',side_effect=lambda args: args[-1].touch()),
                    patch('footagepilot.visual.subprocess.run',side_effect=codex),
                ):
                    if always_invalid:
                        with self.assertRaisesRegex(ValueError,'unknown frames'):
                            plan_visual(spec,output)
                    else:
                        plan_visual(spec,output)
                self.assertEqual(len(prompts),2)
                self.assertIn('copied verbatim from this list: ref-0000',prompts[1])
                self.assertTrue((output/'planner-attempt-1.json').is_file())
                self.assertEqual((output/'edit.json').exists(),not always_invalid)

    def test_plan_uses_only_known_assets_and_complete_collages(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'a.jpg').touch();(p/'score.wav').touch();spec={'assets':[{'id':'a','path':'a.jpg'}],'music':'score.wav','music_timing':{'bpm':120,'offset':0,'provenance':'authored'},'min_seconds':2,'max_seconds':8}
            plan={'title':'TRAVEL','shots':[{'asset_id':'a','beats':4,'fit':'fill','zoom':0}]*2,'panels':[]}
            result=compile_plan(plan,spec,p);self.assertEqual(sum(s['duration'] for s in result['shots']),4)
            bad={**plan,'shots':[{'asset_id':'unknown','beats':4,'fit':'fill','zoom':0}]*2}
            with self.assertRaises(ValueError):compile_plan(bad,spec,p)
            panel={'asset_id':'a','start_beat':0,'beats':2,'x':.25,'y':.25}
            with self.assertRaises(ValueError):compile_plan({**plan,'panels':[panel]},spec,p)
            four=[{**panel,'x':x,'y':y} for x in [.25,.75] for y in [.25,.75]]
            self.assertEqual(len(compile_plan({**plan,'panels':four},spec,p)['overlays']),4)
            with self.assertRaises(ValueError):compile_plan({**plan,'panels':four+[panel]},spec,p)
    def test_unreviewed_comparisons_do_not_become_planner_preferences(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'pending.json').write_text(json.dumps({'human_verdict':'unreviewed','review_notes':'Model thinks this is great'}));(root/'review.json').write_text(json.dumps({'human_verdict':'worse','review_notes':'User requests fewer full-screen graphics'}))
            notes,paths=review_notes({'feedback':['pending.json','review.json']},root)
            self.assertEqual(len(paths),2);self.assertEqual(len(notes),1);self.assertIn('fewer full-screen',notes[0]['review_notes'])

    def test_wipe_planning_requires_resolve_capability(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'a.jpg').touch();(p/'score.wav').touch()
            spec={'assets':[{'id':'a','path':'a.jpg'}],'music':'score.wav','music_timing':{'bpm':120,'offset':0,'provenance':'authored'},'min_seconds':2,'max_seconds':8}
            plan={'title':'Travel','shots':[{'asset_id':'a','beats':4,'fit':'fill','zoom':0,'transition_in':t} for t in ('cut','wipe_left')]}
            with self.assertRaisesRegex(ValueError,'Unknown transition'):compile_plan(plan,spec,p)
            result=compile_plan(plan,{**spec,'native_backend':'resolve'},p)
            self.assertEqual(result['transitions'][0]['filter'],'transition_wipe_left')
            first={**plan,'shots':[dict(row,transition_in='wipe_left') for row in plan['shots']]}
            with self.assertRaisesRegex(ValueError,'First shot'):compile_plan(first,{**spec,'native_backend':'resolve'},p)

    def test_video_source_ranges_checked_against_actual_duration(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'a.mp4').touch();(p/'score.wav').touch()
            spec={'native_backend':'resolve','assets':[{'id':'a','path':'a.mp4'}],'music':'score.wav','music_timing':{'bpm':120,'offset':0,'provenance':'authored'},'min_seconds':2,'max_seconds':8}
            shots=[{'asset_id':'a','beats':4,'fit':'fill','zoom':0,'source_start':at} for at in (1,3)]
            with patch('footagepilot.visual.probe',return_value={'streams':[{'codec_type':'video','duration':'5'}]}):
                result=compile_plan({'title':'Motion','shots':shots},spec,p)
                self.assertEqual([r['source_start'] for r in result['shots']],[1,3])
                with self.assertRaisesRegex(ValueError,'exceeds video'):compile_plan({'title':'Motion','shots':[dict(r,source_start=4) for r in shots]},spec,p)
                with self.assertRaisesRegex(ValueError,'require Resolve'):compile_plan({'title':'Motion','shots':shots},{**spec,'native_backend':'edits'},p)

    def test_zero_tempo_rejected_without_division_error(self):
        with self.assertRaises(ValueError):
            compile_plan({}, {'assets':[],'music_timing':{'bpm':0,'provenance':'invalid'}},Path('.'))
