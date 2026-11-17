"""Behavioral checks for canonical planning, compact exports and packaged JS. No image generation."""
import argparse
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw
import test_pipeline as legacy
p = legacy.p
from split_work_sheet import split_sheet

SKILL = Path(__file__).resolve().parents[1]


class SharedTests(unittest.TestCase):
    def setUp(self):
        legacy.PipelineTests.setUp(self)
        self.plugin.write_text((SKILL/'assets/LL_StandingPictureDirect.js').read_text())

    tearDown = legacy.PipelineTests.tearDown
    fixture = legacy.PipelineTests.fixture

    def compact(self, run, manifest, partial=False, name='export'):
        p.write_json(run/'manifest.json', manifest)
        return p.export_run(argparse.Namespace(manifest=str(run/'manifest.json'), out=str(run/name),
                                               allow_partial=partial, layout='shared', qa_images=False))

    def test_default_plan_preserves_canonical_faces_body_and_source_snapshots(self):
        dest = self.root/'canonical'
        p.plan(argparse.Namespace(out=str(dest), character='phebe', plugin=str(self.plugin), catalog=None, count=None))
        m=p.read_json(dest/'manifest.json')
        self.assertEqual(m['expressions'][0]['name'],'堅定')
        self.assertEqual(m['expressions'][52]['name'],'單眼眨眼')
        self.assertIn('rectangles',m['expressions'][56]['face_prompt'])
        self.assertIn('spirals',m['expressions'][58]['face_prompt'])
        self.assertEqual(m['expressions'][59]['name'],'吐舌眨眼')
        for index in (52, 59):
            wink = m['expressions'][index]
            self.assertEqual(wink['rest_eyes'], 'open')
            self.assertTrue(wink['eyes']['auto'])
            self.assertEqual(wink['eyes']['order'], [0, 1, 2, 3])
            motion = wink['eyes']['motion']
            self.assertEqual(motion['type'], 'single_eye_wink')
            self.assertEqual(motion['moving_eye'], 'reference_selected')
            self.assertEqual([frame['moving_eye'] for frame in motion['frame_states']],
                             ['open', 'half_closed', 'closed', 'half_open'])
            self.assertTrue(all(frame['other_eye']=='open' for frame in motion['frame_states']))
        self.assertEqual(m['expressions'][20]['id'],'21_sigh')
        self.assertEqual(m['expressions'][20]['name'],'嘆氣')
        self.assertEqual(m['body_variants'][20]['mode'],'reuse_default')
        self.assertEqual(m['expressions'][41]['id'],'42_troll_face')
        self.assertEqual(m['expressions'][28]['name'],'誇張大笑')
        self.assertEqual(m['expressions'][29]['name'],'調皮壞笑')
        self.assertEqual(m['expressions'][33]['name'],'使壞咧嘴笑')
        self.assertTrue(m['expressions'][32]['eyes']['auto'])
        self.assertTrue(m['expressions'][47]['eyes']['auto'])
        self.assertEqual(sum(v['mode']=='new_pose' for v in m['body_variants']),43)
        self.assertEqual(sum(v['mode']=='reuse_default' for v in m['body_variants']),17)
        for kind in ('face','body'):
            self.assertEqual(p.digest(dest/m['catalog_source'][kind+'_snapshot']),m['catalog_source'][kind+'_sha256'])

    def test_work_sheet_is_one_column_four_rows_without_recentering(self):
        sheet=Image.new('RGBA',(64,256))
        for i in range(4):ImageDraw.Draw(sheet).rectangle((0,i*64,63,(i+1)*64-1),fill=(40*i,15,23,255))
        path=self.root/'sheet.png';sheet.save(path)
        result=split_sheet(path,64,64,self.root/'split')
        for i,name in enumerate(result['frames']):self.assertEqual(p.rgba(name).getpixel((0,0)),(40*i,15,23,255))
        Image.new('RGBA',(128,128)).save(self.root/'two-by-two.png')
        with self.assertRaisesRegex(ValueError,'one column'):split_sheet(self.root/'two-by-two.png',64,64,self.root/'wrong')

    def test_body_sheet_is_four_columns_and_split_left_to_right(self):
        sheet=Image.new('RGBA',(256,64))
        for i in range(4):ImageDraw.Draw(sheet).rectangle((i*64,0,(i+1)*64-1,63),fill=(40*i,15,23,255))
        path=self.root/'body-sheet.png';sheet.save(path)
        result=split_sheet(path,64,64,self.root/'body-split',4)
        self.assertEqual(result['columns'],4)
        for i,name in enumerate(result['frames']):self.assertEqual(p.rgba(name).getpixel((0,0)),(40*i,15,23,255))

    def test_native_body_export_is_horizontal_bound_and_embedded_without_external_parameters(self):
        run,m=self.fixture(2);m['character_id']='phebe';entry=m['expressions'][0];frames=[]
        for i in range(4):
            name=f'work/body-{i}.png';Image.new('RGBA',(64,64),(40*i,50,80,255)).save(run/name);frames.append(name)
        m['motions']=[{'id':'transition','expression_id':entry['id'],'pose_id':'default','status':'accepted',
                       'frames':frames,'overlay_mode':'baked',
                       'frame_coordinates':[{'eyes':None,'mouth':None}for _ in range(4)],
                       'adapter':{'status':'unbound'},'review':{k:'passed'for k in p.REVIEWS}}]
        m['body_variants'][0].update(mode='new_pose',motion_id='transition')
        result=self.compact(run,m);self.assertTrue(result['complete']);out=run/'export'
        motion=p.read_json(out/'config/motions.json')[0]
        self.assertEqual(motion['layout'],{'columns':4,'rows':1,'frame_width':64,'frame_height':64})
        self.assertEqual(motion['adapter']['status'],'native_bound');self.assertFalse(motion['loop'])
        image=p.rgba(out/motion['image']);self.assertEqual(image.size,(256,64))
        for i in range(4):self.assertEqual(image.getpixel((i*64,0)),(40*i,50,80,255))
        self.assertEqual(p.read_json(out/'config/bodyMotions-readable.json')[0]['columns'],4)
        self.check_compiled_js(out,2)

    def test_compact_export_shares_body_and_atlases_without_static_duplicates(self):
        run,m=self.fixture(2)
        second=m['expressions'][1]
        for rel in [second['base']]+[n for kind in ('eyes','mouth') for n in second[kind]['frames']]:
            im=p.rgba(run/rel);im.putpixel((32,30),(171,81,123,255));im.save(run/rel)
        result=self.compact(run,m);out=run/'export';cfg=p.read_json(out/'config/faceSettings-readable.json')
        self.assertTrue(result['complete']);self.assertEqual(result['counts']['runtime_base_files'],1)
        self.assertEqual(result['counts']['runtime_face_files'],2);self.assertEqual(result['counts']['eye_atlases'],1);self.assertEqual(result['counts']['mouth_atlases'],1)
        assets=out/'runtime/img/pictures/hero'
        self.assertEqual({x.name for x in assets.iterdir()},{'hero_base.png','hero_1.png','hero_2.png','eyes_1.png','mouth_1.png'})
        self.assertFalse((out/'default').exists());self.assertFalse(list((out/'qa').glob('*.png')))
        self.assertEqual(cfg[0]['picture'],'Hero_1');self.assertEqual(cfg[1]['faceImage'],'hero/hero_2')
        for c,e in zip(cfg,m['expressions']):
            image=p.rgba(out/'runtime/img/pictures'/f'{c["baseImage"]}.png');image.alpha_composite(p.rgba(out/'runtime/img/pictures'/f'{c["faceImage"]}.png'),(c['faceX'],c['faceY']))
            self.assertFalse(p.any_pixels(p.ImageChops.difference(image,p.rgba(run/e['base']))))
        qa=p.read_json(out/'qa/pixel-verification.json');self.assertEqual(qa['eye_mouth_combinations'],32)
        self.assertEqual(p.read_json(out/'manifest.json')['engine_verification'],'not_run')

    def test_semtransparent_differences_are_moved_once_and_roundtrip_exactly(self):
        run,m=self.fixture(2)
        files=[run/'masters/default.png']+[run/rel for e in m['expressions'] for rel in [e['base']]+[n for k in ('eyes','mouth') for n in e[k]['frames']]]
        for file in files:
            im=p.rgba(file);im.putpixel((32,30),(239,196,165,253));im.save(file)
        second=m['expressions'][1]
        for rel in [second['base']]+[n for k in ('eyes','mouth') for n in second[k]['frames']]:
            im=p.rgba(run/rel);im.putpixel((32,30),(167,111,75,253));im.save(run/rel)
        m['poses']['default']['sha256']=p.digest(run/'masters/default.png')
        self.compact(run,m);out=run/'export';cfg=p.read_json(out/'config/faceSettings-readable.json')
        base=p.rgba(out/'runtime/img/pictures/hero/hero_base.png');self.assertEqual(base.getpixel((32,30))[3],0)
        for c,e in zip(cfg,m['expressions']):
            image=base.copy();image.alpha_composite(p.rgba(out/'runtime/img/pictures'/f'{c["faceImage"]}.png'),(c['faceX'],c['faceY']))
            self.assertFalse(p.any_pixels(p.ImageChops.difference(image,p.rgba(run/e['base']))))

    def test_partial_has_no_pending_face_or_wrong_historical_phebe_fallback(self):
        run,m=self.fixture(2);m['character_id']='phebe';m['expressions'][1]['status']='pending'
        # Emulate a previous example profile in an otherwise real plugin template.
        source=self.plugin.read_text().replace('const phebeSettings = [];','const phebeSettings = [{picture:"Phebe_2",baseImage:"old/wrong"}];')
        self.plugin.write_text(source);m['target_plugin']=p.probe(self.plugin)
        self.compact(run,m,True);out=run/'export';cfg=p.read_json(out/'config/faceSettings-readable.json')
        self.assertEqual(len(cfg),1);self.assertFalse((out/'runtime/img/pictures/phebe/phebe_2.png').exists())
        script=(out/'plugin'/self.plugin.name).read_text();self.assertNotIn('phebeSettings.forEach(registerFaceSetting);',script)
        self.assertIn('phebeAliases.clear()',script)
        self.check_compiled_js(out,1)

    def check_compiled_js(self,out,expected):
        node=shutil.which('node')
        if not node:
            candidate=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
            if candidate.exists():node=str(candidate)
        if not node:self.skipTest('Node unavailable for actual JS host test')
        subprocess.run([node,str(SKILL/'scripts/test_compiled_plugin.cjs'),str(out),str(expected)],check=True,capture_output=True,text=True)

    def test_exported_js_loads_the_measured_profile_with_zero_external_settings(self):
        run,m=self.fixture(2);m['character_id']='phebe';self.compact(run,m);self.check_compiled_js(run/'export',2)

    def test_sixty_shared_faces_keep_canonical_numbers_and_deduplicated_atlases(self):
        run,m=self.fixture(60);m['character_id']='phebe'
        result=self.compact(run,m);out=run/'export'
        self.assertEqual(result['counts']['runtime_base_files'],1)
        self.assertEqual(result['counts']['runtime_face_files'],60)
        self.assertEqual(result['counts']['runtime_png_files'],63)
        cfg=p.read_json(out/'config/faceSettings-readable.json')
        self.assertEqual([c['picture'] for c in cfg],[f'Phebe_{n}' for n in range(1,61)])
        self.assertEqual(result['counts']['new_B_motions'],0)
        self.assertEqual(p.read_json(out/'qa/pixel-verification.json')['eye_mouth_combinations'],960)
        self.check_compiled_js(out,60)

    def test_duplicate_numbers_wrong_face_roi_and_changed_catalog_fail_before_publish(self):
        run,m=self.fixture(2);m['expressions'][1]['no']=1
        with self.assertRaisesRegex(ValueError,'Duplicate expression numbers'):self.compact(run,m)
        self.assertFalse((run/'export').exists())
        m['expressions'][1]['no']=2
        entry=m['expressions'][1]
        for rel in [entry['base']]+[n for k in ('eyes','mouth') for n in entry[k]['frames']]:
            im=p.rgba(run/rel);im.putpixel((32,30),(111,67,78,255));im.save(run/rel)
        m['poses']['default']['face_roi']=[0,0,8,8]
        with self.assertRaisesRegex(ValueError,'misses expression'):self.compact(run,m)
        del m['poses']['default']['face_roi']
        snapshot=run/m['catalog_source']['face_snapshot'];snapshot.write_text(snapshot.read_text()+'\nchanged')
        with self.assertRaisesRegex(ValueError,'Catalog snapshot changed'):self.compact(run,m)

    def test_b_catalog_requirements_cannot_silently_become_reuse(self):
        run,m=self.fixture(6);m['scope']='full'
        with self.assertRaisesRegex(ValueError,'override_reason'):self.compact(run,m)
        self.assertFalse((run/'export').exists())

    def test_invalid_rest_frame_and_existing_outputs_are_rejected(self):
        run,m=self.fixture();path=run/m['expressions'][0]['eyes']['frames'][0]
        im=p.rgba(path);im.putpixel((14,14),(1,2,3,255));im.save(path)
        with self.assertRaisesRegex(ValueError,'Rest eye0'):self.compact(run,m)
        p.rgba(run/m['expressions'][0]['base']).save(path)
        self.compact(run,m)
        with self.assertRaisesRegex(ValueError,'already exists'):self.compact(run,m)

    def test_probe_and_old_ll_do_not_claim_shared_support(self):
        source=self.plugin.read_text();self.plugin.write_text(source.replace('@param baseImage','@param oldBaseImage'))
        run,m=self.fixture()
        with self.assertRaisesRegex(ValueError,'requires baseImage'):self.compact(run,m)


if __name__=='__main__':unittest.main(verbosity=2)
