"""Synthetic contract tests; no image-provider calls or changes to a game project."""
import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

spec=importlib.util.spec_from_file_location('pipeline',Path(__file__).with_name('ll_portrait_pipeline.py'))
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='ll-portrait-tests-')
        self.root=Path(self.tmp.name)
        # A small metadata fixture for unit tests, not a real game plugin.
        fields='faceSettings picture eyeImage mouthImage eyeX eyeY mouthX mouthY eyeColumns mouthColumns eyeFrameCount mouthFrameCount eyeFrameWidth eyeFrameHeight mouthFrameWidth mouthFrameHeight eyeFrameWait mouthFrameWait eyeAuto eyeIntervalMin eyeIntervalMax eyeFrameOrder mouthFrameOrder'
        self.plugin=self.root/'LL.js'
        self.plugin.write_text('/*:\n * @plugindesc [v1.1.0]\n'+''.join(f' * @param {key}\n' for key in fields.split())+' */')

    def tearDown(self):self.tmp.cleanup()

    def fixture(self,count=1):
        run=self.root/'run'
        p.plan(argparse.Namespace(out=str(run),character='hero',plugin=str(self.plugin),catalog=None,count=count,scope='face-only'))
        manifest=p.read_json(run/'manifest.json')
        master=Image.new('RGBA',(64,64),(239,196,165,255))
        (run/'masters').mkdir();(run/'masks').mkdir()
        master.save(run/'masters/default.png')
        protect=Image.new('L',(64,64));ImageDraw.Draw(protect).point((43,52),fill=255)
        protect.save(run/'masks/default-protect.png')
        face=Image.new('L',(64,64));ImageDraw.Draw(face).rectangle((4,4,59,59),fill=255);face.putpixel((43,52),0)
        face.save(run/'masks/default-face.png')
        manifest['canvas']=[64,64]
        manifest['poses']['default']['sha256']=p.digest(run/'masters/default.png')
        for entry in manifest['expressions']:
            eid=entry['id'];work=run/'work'/eid;work.mkdir(parents=True)
            master.save(work/'base.png')
            entry['status']='accepted';entry['review']={key:'passed' for key in p.REVIEWS}
            for kind,roi,box in [('eyes',[8,8,28,28],(12,12,22,21)),('mouth',[20,36,44,56],(26,41,37,49))]:
                mask=Image.new('L',(64,64));ImageDraw.Draw(mask).rectangle(box,fill=255)
                mask.save(run/entry[kind]['mask']);entry[kind]['roi']=roi
                for i,name in enumerate(entry[kind]['frames']):
                    candidate=master.copy()
                    ImageDraw.Draw(candidate).rectangle((box[0]+1,box[1]+1,box[2]-1,box[3]-1),fill=(30+i*20,40+i*15,50,255))
                    (master.copy() if i==0 else p.compose(master,candidate,mask,protect)).save(run/name)
            entry['eyes']['auto']=False
        for b in manifest['body_variants']:
            b.update(mode='reuse_default',reason='No new gesture in this test')
        p.write_json(run/'manifest.json',manifest)
        return run,manifest

    def export(self,run,manifest,partial=False,name='export'):
        p.write_json(run/'manifest.json',manifest)
        return p.export_run(argparse.Namespace(manifest=str(run/'manifest.json'),out=str(run/name),allow_partial=partial,layout='legacy',qa_images=True))

    def test_plan_has_60_unique_pending_expressions_and_separate_body_decisions(self):
        out=self.root/'full-plan'
        p.plan(argparse.Namespace(out=str(out),character='hero',plugin=str(self.plugin),catalog=None,count=None))
        data=p.read_json(out/'manifest.json')
        self.assertEqual(len(data['expressions']),60);self.assertEqual(len({e['id'] for e in data['expressions']}),60)
        self.assertTrue(all(e['status']=='pending' and e['eyes']['frame_wait']==15 for e in data['expressions']))
        self.assertEqual(sum(b['mode']=='new_pose' for b in data['body_variants']),44);self.assertEqual(sum(b['mode']=='reuse_default' for b in data['body_variants']),16);self.assertEqual(data['expressions'][0]['name'],'堅定');self.assertEqual(data['expressions'][-1]['name'],'吐舌眨眼')
        self.assertFalse(any(out.rglob('*.png')))

    def test_compose_locks_all_outside_channels_and_alpha(self):
        base=Image.new('RGBA',(20,20),(200,150,100,254));candidate=Image.new('RGBA',(20,20),(0,0,0,0))
        mask=Image.new('L',(20,20));mask.putpixel((10,10),128);protect=Image.new('L',(20,20))
        frame=p.compose(base,candidate,mask,protect)
        self.assertEqual(frame.getpixel((10,10))[3],254)
        self.assertEqual(frame.getpixel((0,0)),base.getpixel((0,0)))

    def test_mask_cannot_enter_protected_jaw_even_when_candidate_same(self):
        base=Image.new('RGBA',(20,20),(0,0,0,255));mask=Image.new('L',(20,20));mask.putpixel((12,12),1)
        with self.assertRaisesRegex(ValueError,'protected'):
            p.compose(base,base,mask,mask)

    def test_local_face_patch_uses_fixed_offset_and_keeps_alpha_and_protected_pixels(self):
        base=Image.new('RGBA',(24,24),(200,150,100,254))
        patch=Image.new('RGBA',(8,6),(10,20,30,0));patch.putpixel((2,1),(70,80,90,0))
        mask=Image.new('L',base.size);ImageDraw.Draw(mask).rectangle((6,8,11,11),fill=255)
        protect=Image.new('L',base.size);protect.putpixel((10,10),255);mask.putpixel((10,10),0)
        result=p.compose_patch(base,patch,[5,7,13,13],mask,protect)
        self.assertEqual(result.getpixel((7,8)),(70,80,90,254))
        self.assertEqual(result.getpixel((10,10)),base.getpixel((10,10)))
        self.assertEqual(result.getpixel((0,0)),base.getpixel((0,0)))
        self.assertIsNone(ImageChops.difference(result.getchannel('A'),base.getchannel('A')).getbbox())

    def test_local_face_patch_rejects_resizing_and_masks_outside_the_rectangle(self):
        base=Image.new('RGBA',(24,24),(200,150,100,255))
        mask=Image.new('L',base.size);protect=Image.new('L',base.size)
        with self.assertRaisesRegex(ValueError,'dimensions'):
            p.compose_patch(base,Image.new('RGBA',(9,6)),[5,7,13,13],mask,protect)
        mask.putpixel((4,8),255)
        with self.assertRaisesRegex(ValueError,'outside the local edit rectangle'):
            p.compose_patch(base,Image.new('RGBA',(8,6)),[5,7,13,13],mask,protect)

    def test_extra_jaw_line_inside_roi_but_outside_allowed_mask_is_rejected(self):
        run,m=self.fixture();e=m['expressions'][0];path=run/e['mouth']['frames'][2]
        im=p.rgba(path);im.putpixel((40,52),(0,0,0,255));im.save(path)
        with self.assertRaisesRegex(ValueError,'outside allowed'):
            self.export(run,m)
        self.assertFalse((run/'export').exists())

    def test_runtime_atlases_roundtrip_and_exact_mz_parameter_encoding(self):
        run,m=self.fixture();result=self.export(run,m);self.assertTrue(result['complete'])
        out=run/'export';parameter=p.read_json(out/'config/faceSettings-parameter.json');c=json.loads(parameter[0])
        self.assertEqual(c['mouthX'],'20');self.assertEqual(c['mouthY'],'36');self.assertEqual(c['mouthColumns'],'1')
        self.assertEqual(c['eyeAuto'],'false');self.assertEqual(c['mouthFrameWait'],'15')
        image=p.rgba(out/'runtime/img/pictures/hero/default/01_determined/mouth.png')
        self.assertEqual(image.size,(24,80))
        self.assertEqual(image.getchannel('A').getextrema(),(255,255))
        self.assertFalse((out/'body_language').exists())
        self.assertIn('沿用預設，不另存',(out/'report.html').read_text())
        self.assertIn('16組合局部QA',(out/'report.html').read_text())
        self.assertEqual(len(list((out/'default').glob('*.png'))),1)

    def test_nonopaque_roi_is_not_silently_exported(self):
        run,m=self.fixture();e=m['expressions'][0]
        # Keep alpha invariant across master, base and all full frames, but unsuitable for opaque ROI export.
        for file in [run/'masters/default.png',run/e['base']]+[run/n for k in ('eyes','mouth') for n in e[k]['frames']]:
            im=p.rgba(file);im.putpixel((40,50),(*im.getpixel((40,50))[:3],254));im.save(file)
        m['poses']['default']['sha256']=p.digest(run/'masters/default.png')
        with self.assertRaisesRegex(ValueError,'nonopaque'):
            self.export(run,m)

    def test_changed_roi_border_cannot_be_hidden_by_unchanged_body(self):
        run,m=self.fixture();e=m['expressions'][0];path=run/e['mouth']['mask']
        im=Image.open(path).copy();im.putpixel((20,40),255);im.save(path)
        with self.assertRaisesRegex(ValueError,'two-pixel border'):self.export(run,m)

    def test_partial_does_not_create_pending_placeholder_pngs(self):
        run,m=self.fixture(2);m['expressions'][1]['status']='pending'
        with self.assertRaisesRegex(ValueError,'incomplete'):self.export(run,m)
        result=self.export(run,m,partial=True)
        self.assertFalse(result['complete']);self.assertEqual(result['counts']['exported_A'],1)
        self.assertFalse((run/'export/default'/f'{m["expressions"][1]["id"]}.png').exists())

    def test_visual_review_cannot_be_faked_by_machine_success(self):
        run,m=self.fixture();m['expressions'][0]['review']['seams']='pending'
        with self.assertRaisesRegex(ValueError,'visual review'):self.export(run,m,partial=True)

    def test_unbound_motion_art_is_partial_not_fake_ll_act_support(self):
        run,m=self.fixture();e=m['expressions'][0]
        e['rest_mouth']='open'
        paths=[]
        for i in range(4):
            name=f'work/body{i}.png';p.rgba(run/e['base']).save(run/name);paths.append(name)
        motion={'id':'point','expression_id':e['id'],'pose_id':'default','status':'accepted','frames':paths,
                'frame_duration':15,'loop':False,'end':'hold','overlay_mode':'baked',
                'frame_coordinates':[{'eyes':None,'mouth':None} for _ in range(4)],
                'adapter':{'status':'unbound','config':None,'evidence':None},'review':{k:'passed' for k in p.REVIEWS}}
        m['motions']=[motion];m['body_variants'][0].update(mode='new_pose',motion_id='point')
        with self.assertRaisesRegex(ValueError,'incomplete'):self.export(run,m)
        result=self.export(run,m,partial=True)
        manifest=p.read_json(run/'export/manifest.json')
        self.assertFalse(result['complete']);self.assertTrue(manifest['art_complete']);self.assertFalse(manifest['runtime_complete'])
        self.assertEqual(p.rgba(run/'export/body_language/point.png').size,(256,64))
        self.assertEqual(manifest['items'][0]['rest_mouth'],'open')

    def test_export_checks_target_sha_and_version_contract(self):
        run,m=self.fixture();self.plugin.write_text(self.plugin.read_text()+'\n// changed')
        with self.assertRaisesRegex(ValueError,'plugin changed'):self.export(run,m)
        m['target_plugin']=p.probe(self.plugin);self.plugin.write_text('/* old plugin */');m['target_plugin']=p.probe(self.plugin)
        with self.assertRaisesRegex(ValueError,'faceSettings'):self.export(run,m)

    def test_overlapping_rois_and_unsafe_input_paths_are_rejected(self):
        run,m=self.fixture();m['expressions'][0]['mouth']['roi']=[6,6,48,60]
        with self.assertRaisesRegex(ValueError,'overlap'):self.export(run,m)
        with self.assertRaisesRegex(ValueError,'escapes run'):p.source_path(run,'../LL.js')

    def test_existing_run_or_export_is_never_overwritten(self):
        run,m=self.fixture();self.export(run,m)
        with self.assertRaisesRegex(ValueError,'already exists'):self.export(run,m)
        with self.assertRaisesRegex(ValueError,'already exists'):
            p.plan(argparse.Namespace(out=str(run),character='hero',plugin=str(self.plugin),catalog=None,count=1))

    def test_sixty_exports_keep_distinct_ll_selector_keys_without_fake_b_copies(self):
        run,m=self.fixture(60);result=self.export(run,m)
        configs=p.read_json(run/'export/config/faceSettings-readable.json')
        self.assertTrue(result['complete']);self.assertEqual(result['counts']['exported_A'],60)
        self.assertEqual(result['counts']['runtime_base_files'],60);self.assertEqual(result['counts']['facial_atlases'],120)
        self.assertEqual(len({c['picture'] for c in configs}),60)
        self.assertEqual(result['counts']['new_B_motions'],0);self.assertEqual(result['counts']['reuse_B'],60)
        self.assertFalse((run/'export/body_language').exists())
        self.assertEqual(p.read_json(run/'export/manifest.json')['engine_verification'],'not_run')


if __name__=='__main__':unittest.main(verbosity=2)
