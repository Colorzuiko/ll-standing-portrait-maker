"""Lossless shared-body export, numbered images and an embedded LL JS profile."""
import argparse
import hashlib
import json
import re
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageChops


def diff_mask(a, b):
    channels = ImageChops.difference(a, b).split()
    mask = channels[0]
    for channel in channels[1:]:
        mask = ImageChops.lighter(mask, channel)
    return mask.point(lambda n: 255 if n else 0)


def compiled_plugin(source, configs, provenance, prefix=None, body_motions=None):
    """Install measured defaults before explicit user overrides; never edit a game."""
    begin, end = '/* LL_EXPORTED_PROFILE_BEGIN */', '/* LL_EXPORTED_PROFILE_END */'
    if begin in source:
        if source.count(begin) != 1 or source.count(end) != 1:
            raise ValueError('Ambiguous embedded profile markers')
        source = re.sub(re.escape(begin) + r'.*?' + re.escape(end),
                        'const rawFaceSettings = parseJson(params.faceSettings, []);', source, flags=re.S)
    anchor = 'const rawFaceSettings = parseJson(params.faceSettings, []);'
    if source.count(anchor) != 1:
        raise ValueError('Target needs a reviewed embedded-profile adapter; anchor not unique')
    replacing_phebe = prefix == 'Phebe'
    if replacing_phebe:
        # Canonical numbering differs from the old example profile. Never let an
        # omitted/pending canonical expression fall back to that old artwork.
        source = source.replace('phebeSettings.forEach(registerFaceSetting);',
                                '// Phebe defaults replaced by LL_EXPORTED_FACE_SETTINGS below.')
    payload = json.dumps(configs, ensure_ascii=True, indent=2)
    metadata = json.dumps(provenance, ensure_ascii=True)
    block = (begin + '\n    // Measured export profile; catalog provenance: ' + metadata + '\n'
             '    // Edit this table to change picture/face/eyes/mouth bindings for this export.\n'
             '    const LL_EXPORTED_FACE_SETTINGS = ' + payload + ';\n'
             + ('    if (typeof phebeAliases !== "undefined") phebeAliases.clear();\n' if replacing_phebe else '') +
             '    const LL_USER_FACE_SETTINGS = parseJson(params.faceSettings, []);\n'
             '    const rawFaceSettings = LL_EXPORTED_FACE_SETTINGS.concat(\n'
             '        Array.isArray(LL_USER_FACE_SETTINGS) ? LL_USER_FACE_SETTINGS : []);\n    ' + end)
    source = source.replace(anchor, block)
    body_begin, body_end = '/* LL_EXPORTED_BODY_BEGIN */', '/* LL_EXPORTED_BODY_END */'
    body_anchor = 'const rawBodyMotions = parseJson(params.bodyMotions, []);'
    if body_begin in source:
        if source.count(body_begin)!=1 or source.count(body_end)!=1:
            raise ValueError('Ambiguous embedded body profile markers')
        source = re.sub(re.escape(body_begin)+r'.*?'+re.escape(body_end),body_anchor,source,flags=re.S)
    if body_motions and source.count(body_anchor)!=1:
        raise ValueError('Target needs the native body-sheet JS adapter')
    if source.count(body_anchor)==1:
        body_block = (body_begin+'\n    const LL_EXPORTED_BODY_MOTIONS = '+json.dumps(body_motions or [],ensure_ascii=True,indent=2)+';\n'
                      '    const LL_USER_BODY_MOTIONS = parseJson(params.bodyMotions, []);\n'
                      '    const rawBodyMotions = LL_EXPORTED_BODY_MOTIONS.concat(\n'
                      '        Array.isArray(LL_USER_BODY_MOTIONS) ? LL_USER_BODY_MOTIONS : []);\n    '+body_end)
        source = source.replace(body_anchor,body_block)
    return source


def export_compact(args, p):
    source_manifest = Path(args.manifest).resolve()
    root = source_manifest.parent
    manifest = p.read_json(source_manifest)
    target = p.probe(manifest['target_plugin']['path'])
    p.need(target['shared_faces_declared'], 'Shared export requires baseImage/faceImage/faceX/faceY; use --layout legacy for old LL')
    p.need(target['embedded_profile_anchor'], 'Shared export requires a reviewed embedded JS profile adapter')
    out = Path(args.out).resolve()
    p.need(not out.exists(), 'Output already exists; choose a new export directory')
    character = p.safe_id(manifest['character_id'])
    prefix = manifest.get('command_prefix', character[0].upper() + character[1:])
    p.need(re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', prefix), 'Unsafe command prefix')
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.ll-shared-', dir=out.parent) as temporary:
        work = Path(temporary)
        legacy, staging = work / 'legacy', work / 'shared'
        legacy_args = argparse.Namespace(manifest=str(source_manifest), out=str(legacy),
                                         allow_partial=args.allow_partial,
                                         qa_images=getattr(args, 'qa_images', False))
        p.export_legacy(legacy_args)
        result = p.read_json(legacy / 'manifest.json')
        result.update(layout='shared', command_prefix=prefix,
                      catalog_source=manifest.get('catalog_source'), scope=manifest.get('scope', 'unspecified'))
        old_configs = p.read_json(legacy / 'config/faceSettings-readable.json')
        exported = [e for e in manifest['expressions'] if p.review_ok(e)]
        configs_by_id = dict(zip((e['id'] for e in exported), old_configs))
        groups = defaultdict(list)
        for entry in exported:
            groups[entry['pose_id']].append(entry)
        pictures = staging / 'runtime/img/pictures'
        assets = pictures / character
        assets.mkdir(parents=True)
        shared, face_info = {}, {}
        for pose_id, entries in groups.items():
            p.safe_id(pose_id)
            pose = manifest['poses'][pose_id]
            master = p.rgba(p.source_path(root, pose['master']), manifest['canvas'])
            changed = Image.new('L', master.size)
            bases = {}
            boxes = []
            for entry in entries:
                cfg = configs_by_id[entry['id']]
                base = p.rgba(legacy / 'runtime/img/pictures' / (cfg['picture'] + '.png'))
                bases[entry['id']] = base
                changed = ImageChops.lighter(changed, diff_mask(master, base))
                boxes.extend([entry['eyes']['roi'], entry['mouth']['roi']])
            if changed.getbbox():
                boxes.append(changed.getbbox())
            measured = [max(0, min(b[0] for b in boxes)-2), max(0, min(b[1] for b in boxes)-2),
                        min(master.width, max(b[2] for b in boxes)+2),
                        min(master.height, max(b[3] for b in boxes)+2)]
            box = p.roi_value(pose.get('face_roi', measured), master.size)
            coverage = Image.new('L', master.size)
            p.ImageDraw.Draw(coverage).rectangle((box[0], box[1], box[2]-1, box[3]-1), fill=255)
            p.need(ImageChops.multiply(changed, ImageChops.invert(coverage)).getbbox() is None,
                   'Face ROI misses expression differences; remeasure without moving the character')
            alpha = master.getchannel('A')
            p.need(ImageChops.multiply(changed, alpha.point(lambda n: 255 if n == 0 else 0)).getbbox() is None,
                   'Changing hidden RGB in fully transparent pixels needs a separate blend contract')
            moved = ImageChops.multiply(changed, alpha.point(lambda n: 255 if n < 255 else 0))
            body = master.copy()
            body.putalpha(ImageChops.subtract(alpha, moved))
            body_name = f'{character}_base' + ('' if pose_id == 'default' else '_' + pose_id)
            body.save(assets / (body_name + '.png'), optimize=True)
            for entry in entries:
                face = bases[entry['id']].crop(box)
                face_alpha = face.getchannel('A')
                keep = ImageChops.lighter(face_alpha.point(lambda n: 255 if n == 255 else 0), moved.crop(box))
                face.putalpha(ImageChops.multiply(face_alpha, keep))
                face = Image.composite(face, Image.new('RGBA', face.size), keep)
                face_name = f'{character}_{entry["no"]}'
                face.save(assets / (face_name + '.png'), optimize=True)
                reconstructed = body.copy()
                reconstructed.alpha_composite(p.rgba(assets / (face_name + '.png')), box[:2])
                p.need(not p.any_pixels(ImageChops.difference(reconstructed, bases[entry['id']])),
                       f'Lossless body/face reconstruction failed: {entry["id"]}')
                shared[entry['id']] = (body_name, face_name, reconstructed)
                face_info[entry['id']] = box
        configs, dedup, counters, mapping, comparisons = [], {}, {'eyes': 0, 'mouth': 0}, [], 0
        result_items = {item['id']: item for item in result['items']}
        for entry in exported:
            old_cfg = configs_by_id[entry['id']]
            body_name, face_name, reconstructed = shared[entry['id']]
            box = face_info[entry['id']]
            cfg = dict(old_cfg, picture=f'{prefix}_{entry["no"]}', baseImage=f'{character}/{body_name}',
                       faceImage=f'{character}/{face_name}', faceX=box[0], faceY=box[1])
            sheets = {}
            for kind, field in (('eyes', 'eye'), ('mouth', 'mouth')):
                sheet = p.rgba(legacy / 'runtime/img/pictures' / (old_cfg[field+'Image'] + '.png'))
                sheets[field] = sheet
                key = (kind, entry['pose_id'], tuple(entry[kind]['roi']), sheet.size,
                       hashlib.sha256(sheet.tobytes()).hexdigest())
                if key not in dedup:
                    counters[kind] += 1
                    name = f'{kind}_{counters[kind]}'
                    sheet.save(assets / (name + '.png'), optimize=True)
                    dedup[key] = f'{character}/{name}'
                cfg[field+'Image'] = dedup[key]
            old_base = p.rgba(legacy / 'runtime/img/pictures' / (old_cfg['picture'] + '.png'))
            for ei in range(4):
                for mi in range(4):
                    expected, actual = old_base.copy(), reconstructed.copy()
                    for field, frame in (('eye', ei), ('mouth', mi)):
                        w, h = cfg[field+'FrameWidth'], cfg[field+'FrameHeight']
                        patch = sheets[field].crop((0, frame*h, w, (frame+1)*h))
                        for image in (expected, actual):
                            image.alpha_composite(patch, (cfg[field+'X'], cfg[field+'Y']))
                    p.need(not p.any_pixels(ImageChops.difference(expected, actual)), 'Eye/mouth combination changed after decomposition')
                    comparisons += 1
            configs.append(cfg)
            item = result_items[entry['id']]
            item.update(no=entry['no'], picture=cfg['picture'], static=None, static_render='shared-layers',
                        base_image=cfg['baseImage'], face_image=cfg['faceImage'], face_roi=list(box))
            if item.get('qa'):
                dest = staging / item['qa']
                dest.parent.mkdir(exist_ok=True)
                shutil.copy2(legacy / item['qa'], dest)
            mapping.append({'no': entry['no'], 'id': entry['id'], 'name': entry['name'], **cfg})
        motion_paths, body_configs = {}, []
        for motion in result['motions']:
            old_image = motion['image']
            new_image = f'runtime/img/pictures/{character}/{character}_body_{motion["id"]}.png'
            shutil.copy2(legacy / old_image, staging / new_image)
            motion['image'] = new_image
            motion_paths[old_image] = new_image
            layout=motion['layout']
            body_cfg={'id':motion['id'],'image':f'{character}/{character}_body_{motion["id"]}',
                      'columns':layout['columns'],'frameWidth':layout['frame_width'],'frameHeight':layout['frame_height'],
                      'frameWait':motion['frame_duration'],'end':motion['end']}
            if motion.get('adapter',{}).get('status')=='native_bound':
                body_configs.append(body_cfg)
                motion['command']=f'\\ACT1[{motion["id"]}]'
                motion['loop_command']=motion['command']+'\\loop'
            for key in ('config', 'evidence'):
                rel = motion.get('adapter', {}).get(key)
                if rel:
                    dst = staging / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(legacy / rel, dst)
        for item in result['items']:
            if item['body'].get('image') in motion_paths:
                item['body']['image'] = motion_paths[item['body']['image']]
        p.write_json(staging/'config/faceSettings-readable.json', configs)
        parameter = [json.dumps({k: str(v).lower() if isinstance(v, bool) else str(v) for k, v in c.items()}, ensure_ascii=False) for c in configs]
        p.write_json(staging/'config/faceSettings-parameter.json', parameter)
        p.write_json(staging/'config/expression-mapping.json', mapping)
        p.write_json(staging/'config/motions.json', result['motions'])
        p.write_json(staging/'config/bodyMotions-readable.json',body_configs)
        preview = manifest.get('preview_settings')
        if isinstance(preview, str):
            preview = p.read_json(p.source_path(root, preview))
        preview = preview or {'source': 'suggested; game plugins.js unavailable', 'width': 1280, 'height': 720,
                              'profile': {'prefix': prefix+'_', 'origin': 0, 'x': 0, 'y': 0, 'x2': 1280, 'y2': 0,
                                          'x3': 280, 'y3': 0, 'x4': 1000, 'y4': 0,
                                          'reverse': True, 'scaleX': 100, 'scaleY': 100, 'opacity': 255}}
        p.write_json(staging/'config/preview-settings.json', preview)
        original_bytes = Path(target['path']).read_bytes()
        p.need(hashlib.sha256(original_bytes).hexdigest() == target['sha256'],
               'Target plugin changed during export; re-probe before compiling a profile')
        original_js = original_bytes.decode('utf-8').replace('\r\n', '\n')
        plugin_dest = staging / 'plugin' / Path(target['path']).name
        plugin_dest.parent.mkdir()
        plugin_dest.write_text(compiled_plugin(original_js, configs, manifest.get('catalog_source'), prefix, body_configs), encoding='utf-8')
        result['generated_plugin'] = plugin_dest.relative_to(staging).as_posix()
        result['generated_plugin_sha256'] = p.digest(plugin_dest)
        result['faceSettings_import_required'] = False
        pngs = list(assets.glob('*.png'))
        old_bytes = sum(f.stat().st_size for f in (legacy/'runtime/img/pictures').rglob('*.png'))
        motion_names = {Path(m['image']).name for m in result['motions']}
        new_a_bytes = sum(f.stat().st_size for f in pngs if f.name not in motion_names)
        result['counts'].update(runtime_base_files=len(groups), runtime_face_files=len(exported),
                                eye_atlases=counters['eyes'], mouth_atlases=counters['mouth'],
                                facial_atlases=sum(counters.values()), runtime_png_files=len(pngs),
                                png_files=len(list(staging.rglob('*.png'))),
                                unique_png_content=len({p.digest(f) for f in pngs}))
        result['storage'] = {'comparison_scope': 'A runtime PNG only; excludes B, QA, HTML and JS',
                             'old_full_base_png_bytes': old_bytes, 'shared_A_png_bytes': new_a_bytes,
                             'all_runtime_png_bytes': sum(f.stat().st_size for f in pngs),
                             'saved_percent': round((1-new_a_bytes/old_bytes)*100, 2) if old_bytes else None}
        p.write_json(staging/'qa/pixel-verification.json', {'passed': True, 'rest_roundtrips': len(exported),
                     'eye_mouth_combinations': comparisons, 'rgba_difference_pixels': 0,
                     'engine_verification': 'not_run'})
        p.write_json(staging/'manifest.json', result)
        from shared_report import render_report
        render_report(staging, result, configs, manifest['canvas'], preview)
        p.need(not out.exists(), 'Output appeared while exporting; refusing to overwrite')
        staging.rename(out)
    return {'output': str(out), 'complete': result['complete'], 'counts': result['counts'],
            'storage': result['storage'], 'generated_plugin': result['generated_plugin']}
