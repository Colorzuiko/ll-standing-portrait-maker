"""Independent workflow boundaries and lossless keyframe handling; no provider calls."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image
import body_keyframes as body
import eye_mouth_portrait as eye
import sync_workflow_skills as bundles


class WorkflowToolsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ll-wf-')
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def read(self, relative):
        return json.loads((self.root / relative).read_text(encoding='utf-8'))

    def sheet(self, mode='RGBA', size=(10, 6)):
        im = Image.new(mode, size)
        for y in range(size[1]):
            for x in range(size[0]):
                value = (x*21, y*37, (x+y)*13, 0 if x % 3 == 0 else 128+y)
                im.putpixel((x,y), value if mode == 'RGBA' else value[:3])
        path = self.root / 'sheet.png'
        im.save(path)
        return path, im

    def split(self):
        path, original = self.sheet()
        report = body.split_sheet(path, self.root / 'split', frame_size=8)
        paths = [self.root / 'split' / f'frame_{i}.png' for i in range(1,5)]
        return path, original, report, paths

    def test_body_plan_one_action_has_no_face_run_dependency(self):
        body.plan('hero', self.root / 'plan', [31])
        data = self.read('plan/body-manifest.json')
        self.assertEqual(data['scope'], 'body-only')
        self.assertFalse(data['requires_face_animation_run'])
        self.assertNotIn('expressions', data)
        self.assertNotIn('poses', data)
        self.assertEqual([a['no'] for a in data['actions']], [31])
        self.assertIn('finger', data['actions'][0]['id'])
        self.assertEqual(data['actions'][0]['body_mode'], 'new_pose')
        self.assertEqual(data['generation_layout'], [[1,2],[3,4]])
        self.assertEqual(data['status'], 'planned')
        for kind in ('face', 'body'):
            snapshot = self.root / 'plan' / data['catalog_source'][kind + '_snapshot']
            self.assertEqual(body.digest(snapshot), data['catalog_source'][kind + '_sha256'])
        self.assertFalse(list((self.root / 'plan').rglob('*.png')))

    def test_body_subset_preserves_numbers_and_reuse_is_not_four_placeholders(self):
        body.plan('hero', self.root / 'plan', [31, 1])
        data = self.read('plan/body-manifest.json')
        self.assertEqual([a['no'] for a in data['actions']], [1,31])
        reused = data['actions'][0]
        self.assertEqual(reused['status'], 'reference_only')
        self.assertNotIn('frames', reused)
        self.assertIsNone(reused['generation_method'])

    def test_body_catalog_versions_stay_distinct(self):
        original = body.plan('hero', self.root / 'original')
        alternate = body.plan('hero', self.root / 'alternate', body_catalog=str(
            bundles.ROOT / 'references/body-language-catalog-60-v2.md'))
        self.assertEqual((original['new_pose'], original['reference_only']), (43,17))
        self.assertEqual((alternate['new_pose'], alternate['reference_only']), (35,25))

    def test_bad_body_selection_does_not_create_partial_run(self):
        for numbers in ([31,31], [0], [61]):
            with self.assertRaises(ValueError):
                body.plan('hero', self.root / 'bad-plan', numbers)
            self.assertFalse((self.root / 'bad-plan').exists())
        with self.assertRaises(ValueError):
            body.plan('../hero', self.root / 'bad-id', [31])

    def test_split_preserves_row_order_all_rgba_and_common_padding(self):
        source, original, report, paths = self.split()
        self.assertEqual((self.root / 'split/source-sheet.png').read_bytes(), source.read_bytes())
        rebuilt = Image.new('RGBA', original.size)
        for i, path in enumerate(paths):
            row, col = divmod(i,2)
            with Image.open(path) as frame:
                self.assertEqual(frame.size, (8,8))
                self.assertEqual(frame.getpixel((0,0)), (0,0,0,0))
                cell = frame.crop((1,2,6,5))
            original_cell = original.crop((col*5,row*3,col*5+5,row*3+3))
            self.assertEqual(cell.tobytes(), original_cell.tobytes())
            rebuilt.paste(cell,(col*5,row*3))
            self.assertEqual(report['frames'][i]['padding_left_top'], [1,2])
            self.assertEqual(report['frames'][i]['padding_right_bottom'], [2,3])
        self.assertEqual(rebuilt.tobytes(), original.tobytes())
        self.assertFalse(report['resized'])
        self.assertFalse(report['per_frame_recentered'])
        self.assertEqual(report['visual_review'], 'pending')

    def test_split_rejects_wrong_mode_odd_dimensions_and_oversize_without_output(self):
        for mode, size, final in [('RGB',(10,6),8), ('RGBA',(9,6),8), ('RGBA',(10,6),4)]:
            path, _ = self.sheet(mode,size)
            with self.assertRaises(ValueError):
                body.split_sheet(path,self.root / 'bad-split',final)
            self.assertFalse((self.root / 'bad-split').exists())

    def test_split_refuses_existing_directory_and_preserves_it(self):
        path, _ = self.sheet()
        target = self.root / 'existing'
        target.mkdir()
        sentinel = target / 'keep.txt'
        sentinel.write_text('existing artwork',encoding='utf-8')
        with self.assertRaises(ValueError):
            body.split_sheet(path,target,8)
        self.assertEqual(sentinel.read_text(), 'existing artwork')
        self.assertEqual(len(list(target.iterdir())),1)

    def test_pack_keeps_exact_frames_and_preview_is_only_four_states(self):
        _, _, _, paths = self.split()
        report = body.pack_frames(paths,self.root / 'pack',8,preview=True,duration_ms=350)
        with Image.open(self.root / 'pack/body-4x1.png') as atlas:
            self.assertEqual(atlas.size,(32,8))
            for i, path in enumerate(paths):
                with Image.open(path) as original:
                    self.assertEqual(atlas.crop((i*8,0,(i+1)*8,8)).tobytes(),original.tobytes())
        with Image.open(self.root / 'pack/preview.gif') as preview:
            self.assertEqual(preview.n_frames,4)
            for i in range(4):
                preview.seek(i)
                self.assertEqual(preview.info['duration'],350)
        self.assertEqual(report['runtime_binding'],'unbound')
        self.assertEqual(report['visual_review'],'pending')

    def test_invalid_pack_is_rejected_before_output(self):
        _, _, _, paths = self.split()
        for selected, size, duration in [(paths[:3],8,350), (paths,7,350), (paths,8,355)]:
            with self.assertRaises(ValueError):
                body.pack_frames(selected,self.root / 'bad-pack',size,duration_ms=duration)
            self.assertFalse((self.root / 'bad-pack').exists())

    def test_eye_plan_always_uses_face_only_and_rejects_full(self):
        args = eye.prepare_args(['plan','--character','hero'])
        self.assertEqual(args[-2:],['--scope','face-only'])
        for option in (['--scope','full'], ['--scope=full'], ['--scope','face-only','--scope','full']):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                eye.prepare_args(['plan',*option])

    def test_eye_export_refuses_combined_or_body_tasks(self):
        source = self.root / 'manifest.json'
        args = ['export','--manifest',str(source),'--out',str(self.root / 'export')]
        safe = {'scope':'face-only','motions':[], 'body_variants':[{'mode':'reuse_default'}]}
        source.write_text(json.dumps(safe))
        self.assertEqual(eye.prepare_args(args),args)
        unsafe = [dict(safe,scope='full'), dict(safe,motions=[{'id':'31'}]),
                  dict(safe,body_variants=[{'mode':'new_pose'}]),
                  dict(safe,body_variants=[{'mode':'undecided'}])]
        for manifest in unsafe:
            source.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                eye.prepare_args(args)
        self.assertEqual(eye.prepare_args(['export','--help']),['export','--help'])

    def test_bundles_detect_stale_shared_resources_without_silent_rewrite(self):
        # A miniature repository exercises the real sync/package contract.
        repo = self.root / 'repository'
        for relative in set(p for paths in bundles.SOURCES.values() for p in paths):
            target = repo / relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text('canonical ' + relative,encoding='utf-8')
        bundles.synchronize(root=repo)
        self.assertEqual(bundles.synchronize(check=True,root=repo)['status'],'passed')
        target = repo / 'skills' / bundles.BODY / 'scripts/catalogs.py'
        target.write_text('stale',encoding='utf-8')
        with self.assertRaises(ValueError):
            bundles.synchronize(check=True,root=repo)
        self.assertEqual(target.read_text(),'stale')
        bundles.synchronize(root=repo)
        self.assertEqual(target.read_bytes(),(repo / 'scripts/catalogs.py').read_bytes())
        with self.assertRaises(ValueError):
            bundles.package(self.root / 'incomplete-package',root=repo)
        self.assertFalse((self.root / 'incomplete-package').exists())


if __name__ == '__main__':
    unittest.main()
