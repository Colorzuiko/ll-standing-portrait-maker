#!/usr/bin/env python3
"""Plan, constrain, verify and export LL portrait layers. Does not generate art."""
import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogs import load_catalog

SKILL = Path(__file__).resolve().parents[1]
REVIEWS = ('semantic', 'registration', 'seams', 'combinations', 'transparency')


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def safe_id(value):
    need(isinstance(value, str) and re.fullmatch(r'[a-z0-9][a-z0-9_-]*', value), f'Unsafe ID: {value}')
    return value


def source_path(root, name):
    need(isinstance(name, str) and bool(name), 'Missing input path')
    p = (root / name).resolve()
    need(not Path(name).is_absolute() and p.is_relative_to(root.resolve()), f'Path escapes run: {name}')
    need(p.is_file(), f'Input not found: {name}')
    return p


def rgba(path, size=None):
    with Image.open(path) as im:
        need(im.format == 'PNG' and im.mode == 'RGBA', f'Expected RGBA PNG: {path}')
        need(size is None or im.size == tuple(size), f'Canvas mismatch: {path}, {im.size}, expected {size}')
        return im.copy()


def gray(path, size):
    with Image.open(path) as im:
        need(im.format == 'PNG' and im.mode in ('L', '1') and im.size == tuple(size), f'Expected same-size grayscale PNG: {path}')
        return im.convert('L')


def any_pixels(im):
    return any(channel.getbbox() is not None for channel in im.split())


def binary(im):
    return im.point(lambda v: 255 if v else 0)


def check_mask(mask, protect):
    need(ImageChops.multiply(binary(mask), binary(protect)).getbbox() is None,
         'Allowed mask enters protected pixels; remove protected areas AFTER feathering')


def locked(base, frame, mask, protect):
    need(frame.size == base.size, 'Frame dimensions changed')
    check_mask(mask, protect)
    diff = ImageChops.difference(base, frame)
    outside = ImageChops.invert(binary(mask))
    need(not any(ImageChops.multiply(c, outside).getbbox() for c in diff.split()), 'RGBA changed outside allowed mask')
    need(not any(ImageChops.multiply(c, binary(protect)).getbbox() for c in diff.split()), 'Protected pixels changed')
    need(diff.getchannel('A').getbbox() is None, 'Ordinary face alpha changed')


def compose(base, candidate, mask, protect):
    check_mask(mask, protect)
    need(base.size == candidate.size == mask.size == protect.size, 'Compose inputs must have the same final canvas')
    mixed = Image.composite(candidate.convert('RGB'), base.convert('RGB'), mask).convert('RGBA')
    mixed.putalpha(base.getchannel('A'))
    locked(base, mixed, mask, protect)
    return mixed


def compose_patch(base, patch, rect, mask, protect):
    """Place a local face candidate at its fixed canvas coordinates, then mask."""
    l, t, r, b = roi_value(rect, base.size)
    need(patch.size == (r-l, b-t), 'Local candidate dimensions must match the edit rectangle; no automatic resizing')
    need(mask.size == protect.size == base.size, 'Local compose masks must use the full canvas')
    region = Image.new('L', base.size)
    ImageDraw.Draw(region).rectangle((l, t, r-1, b-1), fill=255)
    need(ImageChops.multiply(mask, ImageChops.invert(region)).getbbox() is None,
         'Allowed mask extends outside the local edit rectangle')
    candidate = base.copy()
    candidate.paste(patch, (l, t))
    return compose(base, candidate, mask, protect)


def probe(path):
    path = Path(path).resolve()
    text = path.read_text(encoding='utf-8')
    params = set(re.findall(r'@param\s+(\w+)', text))
    required = {'faceSettings', 'picture', 'eyeImage', 'mouthImage', 'eyeX', 'eyeY', 'mouthX', 'mouthY',
                'eyeColumns', 'mouthColumns', 'eyeFrameCount', 'mouthFrameCount', 'eyeFrameWidth', 'eyeFrameHeight',
                'mouthFrameWidth', 'mouthFrameHeight', 'eyeFrameWait', 'mouthFrameWait', 'eyeAuto',
                'eyeIntervalMin', 'eyeIntervalMax', 'eyeFrameOrder', 'mouthFrameOrder'}
    version = re.search(r'@plugindesc\s+\[([^\]]+)\]', text)
    commands = sorted(set(re.findall(r'registerCommand\([^,]+,\s*["\']([^"\']+)', text)))
    return {'path': str(path), 'sha256': digest(path), 'version': version.group(1) if version else 'unknown',
            'face_settings_v1_1_declared': required <= params,
            'missing_face_fields': sorted(required - params), 'commands_declared': commands,
            'shared_faces_declared': {'baseImage','faceImage','faceX','faceY'} <= params,
            'embedded_profile_anchor': text.count('const rawFaceSettings = parseJson(params.faceSettings, []);') == 1
                or '/* LL_EXPORTED_PROFILE_BEGIN */' in text,
            'body_sheet_v1_declared': {'bodyMotions','id','image','columns','frameWidth','frameHeight','frameWait','end'} <= params
                and {'playBodyMotion','stopBodyMotion'} <= set(commands)
                and ('const rawBodyMotions = parseJson(params.bodyMotions, []);' in text
                     or '/* LL_EXPORTED_BODY_BEGIN */' in text),
            'body_atlas_candidate_declared': bool(re.search(r'@param\s+(?:actions|motions|bodyAnimations)\b', text)),
            'runtime_verified': False, 'note': 'Static source evidence only; body atlas interface requires manual inspection and runtime testing.'}


def plan(args):
    out = Path(args.out).resolve()
    need(not out.exists(), 'Plan directory already exists; use a new run')
    character = safe_id(args.character)
    catalog, provenance = load_catalog(args.catalog, getattr(args, 'body_catalog', None))
    count = args.count if args.count is not None else len(catalog)
    need(isinstance(catalog, list) and 0 < count <= len(catalog), 'Invalid catalog/count')
    catalog = catalog[:count]
    ids = [safe_id(item['id']) for item in catalog]
    need(len(set(ids)) == count, 'Duplicate expression IDs')
    target = probe(args.plugin)
    expressions = []
    for i, item in enumerate(catalog, 1):
        eid = item['id']
        layer = lambda kind: {'mask': f'masks/{eid}-{kind}.png', 'roi': None,
                              'frames': [f'work/{eid}/{kind}{n}.png' for n in range(4)], 'frame_wait': 15, 'order':[0,1,2,3]}
        eyes = {**layer('eyes'), 'auto': item.get('eye_auto', item.get('rest_eyes') != 'closed'), 'interval_min': 180, 'interval_max': 300}
        if item.get('eye_motion'):
            eyes['motion'] = item['eye_motion']
        mouth = layer('mouth')
        if item.get('mouth_motion'):
            mouth['motion'] = item['mouth_motion']
        expressions.append({'no': item.get('no', i), 'id': eid, 'name': item['name'], 'face_prompt': item['face'],
                            'pose_id': 'default', 'status': 'pending', 'base': f'work/{eid}/base.png',
                            'rest_eyes': item.get('rest_eyes', 'open'), 'rest_mouth': item.get('rest_mouth', 'closed'),
                            'eyes': eyes, 'mouth': mouth, 'review': {key: 'pending' for key in REVIEWS}})
    manifest = {'schema_version': 1, 'character_id': character, 'canvas': [720, 720], 'expected_count': count,
                'source_basis': 'SKILL_3RD canonical catalogs; fixed-pose facial layers',
                'catalog_source': provenance, 'scope': getattr(args, 'scope', 'full'),
                'target_plugin': target, 'generation_log': [],
                'poses': {'default': {'master': 'masters/default.png', 'sha256': None,
                                      'face_mask': 'masks/default-face.png', 'protect': 'masks/default-protect.png'}},
                'expressions': expressions,
                'body_variants': [{'expression_id': item['id'],
                                   'mode': 'reuse_default' if getattr(args, 'scope', 'full') == 'face-only' else item.get('body_mode', 'undecided'),
                                   'catalog_mode': item.get('body_mode', 'undecided'),
                                   'reason': 'Explicit face-only scope; B not included' if getattr(args, 'scope', 'full') == 'face-only' else (item.get('body_hint', '') if item.get('body_mode') == 'reuse_default' else ''),
                                   'motion_id': None, 'body_hint': item.get('body_hint', ''),
                                   'body_prompt': item.get('body_prompt', '')} for item in catalog], 'motions': []}
    out.mkdir(parents=True)
    for kind in ('face', 'body'):
        if provenance.get(kind+'_path'):
            destination = out/'sources'/f'{kind}-catalog{Path(provenance[kind+"_path"]).suffix}'
            destination.parent.mkdir(exist_ok=True)
            shutil.copy2(provenance[kind+'_path'], destination)
            provenance[kind+'_snapshot'] = destination.relative_to(out).as_posix()
    write_json(out / 'manifest.json', manifest)
    return {'manifest': str(out / 'manifest.json'), 'planned_expressions': count, 'status': 'pending', 'target': target}


def review_ok(entry):
    return entry.get('status') == 'accepted' and all(entry.get('review', {}).get(k) == 'passed' for k in REVIEWS)


def roi_value(value, size):
    need(isinstance(value, list) and len(value) == 4 and all(type(v) is int for v in value), 'ROI must be four integer coordinates')
    l, t, r, b = value
    need(0 <= l < r <= size[0] and 0 <= t < b <= size[1] and r-l >= 5 and b-t >= 5, 'ROI outside canvas or too small for edge guards')
    return tuple(value)


def integer(value, minimum=1):
    need(type(value) is int and value >= minimum, f'Expected integer >= {minimum}: {value}')
    return value


def load_expression(root, manifest, entry):
    size = manifest['canvas']
    pose = manifest['poses'][entry['pose_id']]
    master_path = source_path(root, pose['master'])
    need(pose.get('sha256') == digest(master_path), f'Unfrozen or changed master: {entry["pose_id"]}')
    master = rgba(master_path, size)
    face_mask = gray(source_path(root, pose['face_mask']), size)
    protect = gray(source_path(root, pose['protect']), size)
    base = rgba(source_path(root, entry['base']), size)
    locked(master, base, face_mask, protect)
    layers = {}
    for kind in ('eyes', 'mouth'):
        spec = entry[kind]
        roi = roi_value(spec['roi'], size)
        mask = gray(source_path(root, spec['mask']), size)
        check_mask(mask, protect)
        region = Image.new('L', tuple(size))
        ImageDraw.Draw(region).rectangle((roi[0], roi[1], roi[2]-1, roi[3]-1), fill=255)
        need(ImageChops.multiply(mask, ImageChops.invert(region)).getbbox() is None, f'{kind} mask outside ROI')
        crop_mask = mask.crop(roi)
        w, h = crop_mask.size
        border = crop_mask.copy()
        ImageDraw.Draw(border).rectangle((2, 2, w-3, h-3), fill=0)
        need(border.getbbox() is None, f'{kind} ROI needs an unchanged two-pixel border')
        need(base.crop(roi).getchannel('A').getextrema() == (255, 255), f'{kind} ROI crosses nonopaque base; redesign ROI/matting before freezing')
        need(isinstance(spec['frames'], list) and len(spec['frames']) == 4, 'Each atlas must have exactly four full-canvas frames')
        frames = [rgba(source_path(root, name), size) for name in spec['frames']]
        for frame in frames:
            locked(base, frame, mask, protect)
        integer(spec['frame_wait'])
        need(spec['frame_wait']<=6000, 'Frame wait exceeds LL v1.1 limit')
        order=spec.get('order',[0,1,2,3])
        need(isinstance(order,list) and len(order)>0 and all(type(n) is int and 0<=n<4 for n in order), 'Invalid frame order')
        if kind == 'eyes':
            need(type(spec['auto']) is bool, 'eyes.auto must be boolean')
            integer(spec['interval_min'], 0); integer(spec['interval_max'], 0)
            need(spec['interval_min'] <= spec['interval_max'], 'Invalid blink gap range')
            need(spec['interval_max']<=6000, 'Blink interval exceeds LL v1.1 limit')
        layers[kind] = {'roi': roi, 'mask': mask, 'frames': frames, 'patches': [f.crop(roi) for f in frames]}
    e, m = layers['eyes']['roi'], layers['mouth']['roi']
    need(e[2] <= m[0] or m[2] <= e[0] or e[3] <= m[1] or m[3] <= e[1], 'Eye/mouth ROIs overlap; use a dedicated combined/occlusion adapter')
    union = ImageChops.lighter(layers['eyes']['mask'], layers['mouth']['mask'])
    need(not any_pixels(ImageChops.difference(base, rebuild(base, layers, 0, 0))),
         'Rest eye0/mouth0 must reconstruct the accepted expression base exactly')
    for ei in range(4):
        for mi in range(4):
            frame = rebuild(base, layers, ei, mi)
            locked(base, frame, union, protect)
            expected = base.copy()
            for kind, n in (('eyes', ei), ('mouth', mi)):
                roi = layers[kind]['roi']
                expected.paste(layers[kind]['frames'][n].crop(roi), roi[:2])
            need(not any_pixels(ImageChops.difference(expected, frame)), 'Source-over round-trip differs from accepted frames')
    return {'base': base, 'layers': layers, 'master_sha256': pose['sha256']}


def rebuild(base, layers, eye, mouth):
    frame = base.copy()
    for kind, n in (('eyes', eye), ('mouth', mouth)):
        frame.alpha_composite(layers[kind]['patches'][n], layers[kind]['roi'][:2])
    return frame


def contact_image(art):
    e, m = art['layers']['eyes']['roi'], art['layers']['mouth']['roi']
    w, h = art['base'].size
    box = (max(0, min(e[0],m[0])-25), max(0,min(e[1],m[1])-25), min(w,max(e[2],m[2])+25), min(h,max(e[3],m[3])+25))
    board = Image.new('RGB', (640, 704), '#e4e8e0')
    draw = ImageDraw.Draw(board)
    for eye in range(4):
        for mouth in range(4):
            im = rebuild(art['base'], art['layers'], eye, mouth).crop(box)
            bg = Image.new('RGBA', im.size, '#f6f2e9' if (eye+mouth)%2 else '#24343c')
            bg.alpha_composite(im)
            bg.thumbnail((160, 150))
            x, y = mouth*160+(160-bg.width)//2, eye*176
            board.paste(bg.convert('RGB'), (x,y))
            draw.text((mouth*160+5, y+153), f'eye {eye} / mouth {mouth}', fill='#16343e')
    return board


def atlas(frames, columns=1):
    w, h = frames[0].size
    need(columns in (1,4) and len(frames)==4, 'Four frames require one or four columns')
    need(all(f.size == (w,h) for f in frames), 'Atlas frame dimensions differ')
    im = Image.new('RGBA', (w*columns,4*h//columns))
    for i, frame in enumerate(frames):
        im.paste(frame, ((i%columns)*w,(i//columns)*h))
    return im


def settings(entry, layers, stem):
    result = {'picture': f'{stem}/base'}
    for kind, prefix in (('eyes','eye'), ('mouth','mouth')):
        l, t, r, b = layers[kind]['roi']
        result.update({f'{prefix}Image': f'{stem}/{kind}', f'{prefix}X':l, f'{prefix}Y':t,
                       f'{prefix}Columns':1, f'{prefix}FrameCount':4, f'{prefix}FrameWidth':r-l,
                       f'{prefix}FrameHeight':b-t, f'{prefix}FrameWait':entry[kind]['frame_wait'],
                       f'{prefix}FrameOrder':','.join(map(str,entry[kind].get('order',[0,1,2,3])))})
    result.update(eyeAuto=entry['eyes']['auto'], eyeIntervalMin=entry['eyes']['interval_min'], eyeIntervalMax=entry['eyes']['interval_max'])
    return result


def validate_manifest(manifest):
    need(manifest.get('schema_version') == 1, 'Unknown manifest schema')
    safe_id(manifest['character_id'])
    size = manifest['canvas']
    need(len(size)==2 and all(type(n) is int and n>0 for n in size), 'Invalid canvas')
    entries = manifest['expressions']
    ids = [safe_id(e['id']) for e in entries]
    need(len(set(ids))==len(ids) and len(entries)==manifest['expected_count'] and len(entries)>0, 'Expression count or IDs inconsistent')
    numbers = [integer(e['no']) for e in entries]
    need(len(set(numbers)) == len(numbers), 'Duplicate expression numbers would overwrite numbered files')
    return entries


def render_report(path, result):
    esc = lambda x: html.escape(str(x), quote=True)
    rows = []
    for item in result['items']:
        a = f'<img src="{esc(item["static"])}" alt="{esc(item["name"])}">' if item.get('static') else '待完成，沒有占位圖片'
        b = item['body']
        body = ('沿用預設，不另存：'+esc(b.get('reason',''))) if b.get('mode')=='reuse_default' else esc(b.get('mode','undecided'))
        if b.get('image'):
            body = f'<img src="{esc(b["image"])}" alt="肢體動作圖集"><p>{esc(b.get("runtime_status"))}</p>'
        qa = f'<p><a href="{esc(item["qa"])}">16組合局部QA</a></p>' if item.get('qa') else ''
        rows.append(f'<article data-status="{esc(item["status"])}"><h2>{esc(item["id"])} · {esc(item["name"])}</h2><p>{esc(item["status"])}</p><div class="pair"><section>{a}{qa}</section><section>{body}</section></div></article>')
    text = '''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>LL立繪素材驗收</title><style>body{font:15px/1.7 system-ui;background:#f1f1e9;color:#20363c;max-width:1100px;margin:auto;padding:24px}h1{font-size:30px}article{background:#fff;border:1px solid #ccc;padding:18px;margin:16px 0}h2{font-size:19px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}img{max-width:100%;max-height:520px;object-fit:contain;background:repeating-conic-gradient(#ddd 0 25%,#fff 0 50%) 0/20px 20px}pre{white-space:pre-wrap}select{padding:8px}@media(max-width:600px){.pair{grid-template-columns:1fr}}</style><h1>LL立繪素材驗收</h1>'''
    text += f'<p>完成：{esc(result["complete"])}；美術：{esc(result["art_complete"])}；插件設定對應：{esc(result["runtime_complete"])}；引擎實測：{esc(result["engine_verification"])}</p><pre>{esc(json.dumps(result["counts"],ensure_ascii=False,indent=2))}</pre>'
    text += '<label>篩選 <select id="filter"><option value="all">全部</option><option value="exported">已匯出A</option><option value="pending">未完成</option></select></label>'
    text += ''.join(rows) + '''<script>document.getElementById('filter').onchange=function(){for(const el of document.querySelectorAll('article'))el.hidden=this.value!=='all'&&el.dataset.status!==this.value;};</script></html>'''
    path.write_text(text, encoding='utf-8')


def export_legacy(args):
    root = Path(args.manifest).resolve().parent
    manifest = read_json(args.manifest)
    entries = validate_manifest(manifest)
    for kind in ('face', 'body'):
        provenance = manifest.get('catalog_source', {})
        if provenance.get(kind+'_snapshot'):
            need(digest(source_path(root, provenance[kind+'_snapshot'])) == provenance[kind+'_sha256'],
                 'Catalog snapshot changed; review and re-plan instead of silently changing expression meanings')
    target = probe(manifest['target_plugin']['path'])
    need(target['sha256']==manifest['target_plugin']['sha256'], 'Target plugin changed; inspect and refresh capability snapshot')
    need(target['face_settings_v1_1_declared'], 'Target does not declare the supported LL faceSettings contract')
    accepted = [e for e in entries if review_ok(e)]
    for e in entries:
        if e.get('status')=='accepted':
            need(review_ok(e), f'Incomplete visual review: {e["id"]}')
            load_expression(root, manifest, e)
    a_complete = len(accepted)==manifest['expected_count']
    ids = {e['id'] for e in entries}
    variants = manifest.get('body_variants', [])
    need(len(variants)==len(entries) and {v['expression_id'] for v in variants}==ids, 'B decisions must cover every A exactly once')
    motions = {safe_id(m['id']):m for m in manifest.get('motions',[])}
    need(len(motions)==len(manifest.get('motions',[])), 'Duplicate motion IDs')
    body_complete = True; runtime_complete = a_complete
    used = set()
    for v in variants:
        if manifest.get('scope') == 'full' and v.get('catalog_mode') == 'new_pose' and v.get('mode') != 'new_pose':
            need(bool(str(v.get('override_reason', '')).strip()),
                 'Required catalog body pose changed to reuse; record the explicit user override_reason or use an authorized face-only scope')
        mode = v['mode']
        if mode=='reuse_default':
            need(bool(str(v.get('reason','')).strip()), 'reuse_default needs a reason')
        elif mode=='new_pose':
            m = motions.get(v.get('motion_id'))
            if not m or not review_ok(m):
                body_complete=False; runtime_complete=False; continue
            need(a_complete, 'Finish A before accepting/exporting new B motion')
            need(m['expression_id']==v['expression_id'], 'Motion expression mismatch')
            pose=manifest['poses'].get(m.get('pose_id'))
            need(pose is not None, 'Motion needs its own frozen pose contract')
            need(pose.get('sha256')==digest(source_path(root,pose['master'])), 'Motion pose master changed or not frozen')
            need(m.get('overlay_mode')=='baked', 'Independent body overlays require a dedicated verified adapter; generic export supports baked only')
            need(isinstance(m['frames'],list) and len(m['frames'])==4, 'Body motion needs four full frames')
            for name in m['frames']:
                rgba(source_path(root,name),manifest['canvas'])
            m.setdefault('frame_duration',15)
            m.setdefault('loop',False)
            m.setdefault('end','hold')
            m.setdefault('columns',4)
            need(m['columns'] in (1,4), 'Body columns must be 4 (horizontal), or explicitly 1 for a legacy sheet')
            integer(m['frame_duration'])
            need(type(m['loop']) is bool and m.get('end') in ('hold','restore'), 'Invalid motion playback mode')
            need(len(m.get('frame_coordinates',[]))==4, 'Record coordinates/explicit baked nulls for all motion frames')
            for pos in m['frame_coordinates']:
                need(pos.get('eyes') is None and pos.get('mouth') is None, 'Baked frames must not request extra facial overlays')
            adapter = m.get('adapter',{})
            if adapter.get('status')=='verified':
                source_path(root,adapter.get('config'));source_path(root,adapter.get('evidence'))
            elif target.get('body_sheet_v1_declared') and adapter.get('status','unbound') in ('unbound','native_bound'):
                m['adapter']={'status':'native_bound','contract':'LL body-sheet v1',
                              'target_sha256':target['sha256'],'engine_verification':'not_run'}
            else:
                runtime_complete=False
            used.add(m['id'])
        else:
            body_complete=False; runtime_complete=False
    complete = a_complete and body_complete and runtime_complete
    need(args.allow_partial or complete, 'Run is incomplete (A/B/reviews/runtime adapter); use --allow-partial for clearly marked progress only')
    out = Path(args.out).resolve()
    need(not out.exists(), 'Output already exists; choose a new export directory')
    out.parent.mkdir(parents=True,exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.ll-export-',dir=out.parent))
    result = {'schema_version':1,'character_id':manifest['character_id'],'source_manifest':str(Path(args.manifest).resolve()),
              'target_plugin':target,'complete':complete,'art_complete':a_complete and body_complete,'runtime_complete':runtime_complete,
              'engine_verification':'not_run',
              'counts':{},'items':[],'motions':[]}
    configs = []
    try:
        by_variant = {v['expression_id']:v for v in variants}
        exported = {e['id'] for e in accepted}
        for e in entries:
            body = dict(by_variant[e['id']])
            item = {'id':e['id'],'name':e['name'],'status':'pending','static':None,'body':body}
            if e['id'] in exported:
                art = load_expression(root,manifest,e)
                stem = f'{manifest["character_id"]}/default/{e["id"]}'
                destination = staging/'runtime/img/pictures'/stem
                destination.mkdir(parents=True)
                art['base'].save(destination/'base.png')
                for kind in ('eyes','mouth'):
                    atlas(art['layers'][kind]['patches']).save(destination/f'{kind}.png')
                configs.append(settings(e,art['layers'],stem))
                static = staging/'default'/f'{e["id"]}.png';static.parent.mkdir(exist_ok=True)
                rebuild(art['base'],art['layers'],0,0).save(static)
                qa = None
                if getattr(args, 'qa_images', False):
                    qa = staging/'qa'/f'{e["id"]}-combinations.png';qa.parent.mkdir(exist_ok=True)
                    contact_image(art).save(qa)
                item.update(status='exported',static=static.relative_to(staging).as_posix(),qa=qa.relative_to(staging).as_posix() if qa else None,
                            review=e['review'],rest_eyes=e.get('rest_eyes'),rest_mouth=e.get('rest_mouth'),
                            master_sha256=art['master_sha256'],coordinates={k:list(v['roi']) for k,v in art['layers'].items()},
                            distinct_frames={k:len({hashlib.sha256(p.tobytes()).hexdigest() for p in v['patches']}) for k,v in art['layers'].items()})
            else:
                item['source_status']=e.get('status','pending')
            result['items'].append(item)
        for mid in sorted(used):
            m = motions[mid]
            frames = [rgba(source_path(root,n),manifest['canvas']) for n in m['frames']]
            folder = staging/'body_language';folder.mkdir(exist_ok=True)
            dest = folder/f'{mid}.png';atlas(frames,m['columns']).save(dest)
            record = json.loads(json.dumps({k:v for k,v in m.items() if k not in ('frames',)}))
            record['image']=dest.relative_to(staging).as_posix()
            record['layout']={'columns':m['columns'],'rows':4//m['columns'],
                              'frame_width':manifest['canvas'][0],'frame_height':manifest['canvas'][1]}
            if m.get('adapter',{}).get('status')=='verified':
                adapter_dir=staging/'config/adapters';adapter_dir.mkdir(parents=True,exist_ok=True)
                for key in ('config','evidence'):
                    src=source_path(root,m['adapter'][key]);d=adapter_dir/f'{mid}-{key}{src.suffix}'
                    shutil.copy2(src,d);record['adapter'][key]=d.relative_to(staging).as_posix()
            result['motions'].append(record)
            for item in result['items']:
                if item['body'].get('motion_id')==mid:
                    item['body'].update(image=record['image'],runtime_status=m.get('adapter',{}).get('status','unbound'))
        write_json(staging/'config/faceSettings-readable.json',configs)
        parameter=[json.dumps({k:str(v).lower() if isinstance(v,bool) else str(v) for k,v in c.items()},ensure_ascii=False) for c in configs]
        write_json(staging/'config/faceSettings-parameter.json',parameter)
        write_json(staging/'config/motions.json',result['motions'])
        pngs=list(staging.rglob('*.png'))
        result['counts']={'expected_A':manifest['expected_count'],'exported_A':len(accepted),'new_B_motions':len(used),
                          'reuse_B':sum(v['mode']=='reuse_default' for v in variants),'runtime_base_files':len(accepted),
                          'facial_atlases':2*len(accepted),'png_files':len(pngs),'unique_png_content':len({digest(p) for p in pngs})}
        write_json(staging/'manifest.json',result)
        render_report(staging/'report.html',result)
        need(not out.exists(),'Output appeared while exporting; refusing to overwrite')
        staging.rename(out)
    except BaseException:
        shutil.rmtree(staging,ignore_errors=True)
        raise
    return {'output':str(out),'complete':complete,'counts':result['counts']}


def export_run(args):
    if getattr(args, 'layout', 'shared') == 'legacy':
        return export_legacy(args)
    from shared_export import export_compact
    return export_compact(args, SimpleNamespace(**globals()))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('probe');p.add_argument('--plugin',required=True)
    p=sub.add_parser('plan');p.add_argument('--character',required=True);p.add_argument('--plugin',required=True);p.add_argument('--out',required=True);p.add_argument('--count',type=int);p.add_argument('--catalog');p.add_argument('--body-catalog');p.add_argument('--scope',choices=['full','face-only'],default='full')
    p=sub.add_parser('compose')
    for key in ('base','candidate','mask','protect','out'):p.add_argument('--'+key,required=True)
    p.add_argument('--rect',type=int,nargs=4,metavar=('LEFT','TOP','RIGHT','BOTTOM'),
                   help='Place a same-size local face patch at this full-canvas rectangle before masking')
    p=sub.add_parser('contact');p.add_argument('--manifest',required=True);p.add_argument('--id',required=True);p.add_argument('--out',required=True)
    p=sub.add_parser('export');p.add_argument('--manifest',required=True);p.add_argument('--out',required=True);p.add_argument('--allow-partial',action='store_true')
    p.add_argument('--layout',choices=['shared','legacy'],default='shared');p.add_argument('--qa-images',action='store_true')
    args=parser.parse_args()
    try:
        if args.command=='probe':result=probe(args.plugin)
        elif args.command=='plan':result=plan(args)
        elif args.command=='export':result=export_run(args)
        else:
            out=Path(args.out);need(not out.exists(),'Output exists; choose a new path')
            if args.command=='compose':
                base=rgba(args.base);mask=gray(args.mask,base.size);protect=gray(args.protect,base.size)
                if args.rect is not None:
                    image=compose_patch(base,rgba(args.candidate),args.rect,mask,protect)
                else:
                    image=compose(base,rgba(args.candidate,base.size),mask,protect)
            else:
                manifest=read_json(args.manifest);entries=validate_manifest(manifest)
                entry=next((e for e in entries if e['id']==args.id),None);need(entry,'Unknown expression ID')
                image=contact_image(load_expression(Path(args.manifest).resolve().parent,manifest,entry))
            out.parent.mkdir(parents=True,exist_ok=True)
            with out.open('xb') as stream:image.save(stream,format='PNG')
            result={'output':str(out)}
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError,TypeError) as error:
        print(f'ERROR: {error}',file=sys.stderr)
        raise SystemExit(1)


if __name__=='__main__':main()
