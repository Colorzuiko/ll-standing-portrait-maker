#!/usr/bin/env python3
"""Plan independent body keyframes; split one 2x2 sheet and pack accepted frames."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from PIL import Image


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def new_output(path):
    out = Path(path).resolve()
    need(not out.exists(), 'Output exists; choose a new run/output directory')
    return out


def rgba(path):
    with Image.open(path) as image:
        need(image.format == 'PNG' and image.mode == 'RGBA', f'Expected RGBA PNG: {path}')
        return image.copy()


def plan(character, out, numbers=None, catalog=None, body_catalog=None):
    from catalogs import load_catalog
    need(re.fullmatch(r'[a-z0-9][a-z0-9_-]*', character), 'Use a lowercase character ID')
    out = new_output(out)
    items, provenance = load_catalog(catalog, body_catalog)
    wanted = None if numbers is None else set(numbers)
    need(wanted is None or len(wanted) == len(numbers), 'Duplicate action numbers')
    available = {item['no'] for item in items}
    need(wanted is None or wanted <= available, 'Unknown action number')
    chosen = [item for item in items if wanted is None or item['no'] in wanted]
    actions = []
    for item in chosen:
        mode = item.get('body_mode', 'undecided')
        action = {'no': item['no'], 'id': item['id'], 'name': item['name'],
                  'expression_prompt': item['face'], 'body_mode': mode,
                  'body_hint': item.get('body_hint', ''), 'body_prompt': item.get('body_prompt', ''),
                  'status': 'reference_only' if mode == 'reuse_default' else 'pending',
                  'generation_method': None if mode == 'reuse_default' else 'one_canvas_full_frame_2x2',
                  'stages': [], 'review': {'semantics': 'pending', 'hands_and_contact': 'pending',
                                           'continuity': 'pending', 'transparency': 'pending'}}
        if mode != 'reuse_default':
            action['frames'] = []
        actions.append(action)
    manifest = {'schema_version': 1, 'workflow': 'body-keyframes', 'scope': 'body-only',
                'character_id': character, 'canvas': [720, 720], 'generation_layout': [[1, 2], [3, 4]],
                'catalog_source': provenance, 'actions': actions, 'generation_log': [],
                'requires_face_animation_run': False, 'independent_eye_mouth_atlases': 'not_in_scope',
                'runtime_binding': 'unbound', 'status': 'planned'}
    out.mkdir(parents=True)
    (out / 'sources').mkdir()
    for kind in ('face', 'body'):
        if provenance.get(kind + '_path'):
            source = Path(provenance[kind + '_path'])
            target = out / 'sources' / f'{kind}-catalog{source.suffix}'
            shutil.copy2(source, target)
            provenance[kind + '_snapshot'] = target.relative_to(out).as_posix()
    write_json(out / 'body-manifest.json', manifest)
    return {'manifest': str(out / 'body-manifest.json'), 'actions': len(actions),
            'new_pose': sum(a['body_mode'] == 'new_pose' for a in actions),
            'reference_only': sum(a['body_mode'] == 'reuse_default' for a in actions),
            'requires_face_animation_run': False, 'status': 'planned_not_generated'}


def split_sheet(image, out, frame_size=720):
    need(type(frame_size) is int and frame_size > 0, 'Frame size must be a positive integer')
    out = new_output(out)
    source = rgba(image)
    need(source.width % 2 == 0 and source.height % 2 == 0, '2x2 sheet dimensions must be even')
    width, height = source.width // 2, source.height // 2
    need(width <= frame_size and height <= frame_size,
         'Native cell exceeds final canvas; record one common whole-sheet normalization first. No automatic resizing.')
    offset = ((frame_size-width)//2, (frame_size-height)//2)
    frames = []
    reconstruction = Image.new('RGBA', source.size)
    records = []
    for index in range(4):
        row, column = divmod(index, 2)
        box = (column*width, row*height, (column+1)*width, (row+1)*height)
        cell = source.crop(box)
        frame = Image.new('RGBA', (frame_size, frame_size))
        frame.paste(cell, offset)
        need(frame.crop((offset[0],offset[1],offset[0]+width,offset[1]+height)).tobytes() == cell.tobytes(),
             'Padding altered source pixels')
        reconstruction.paste(cell, box[:2])
        frames.append(frame)
        records.append({'frame': index+1, 'row': row, 'column': column, 'source_box': list(box),
                        'file': f'frame_{index+1}.png', 'padding_left_top': list(offset),
                        'padding_right_bottom': [frame_size-width-offset[0], frame_size-height-offset[1]],
                        'source_pixels_unchanged': True})
    need(reconstruction.tobytes() == source.tobytes(), 'Source reconstruction failed')
    out.mkdir(parents=True)
    shutil.copy2(image, out / 'source-sheet.png')
    for frame, entry in zip(frames, records):
        frame.save(out / entry['file'])
        entry['sha256'] = digest(out / entry['file'])
    report = {'workflow': 'body-keyframes', 'generation_layout': [[1,2],[3,4]],
              'source': 'source-sheet.png', 'source_sha256': digest(image),
              'source_size': list(source.size), 'native_cell_size': [width,height],
              'frame_size': [frame_size,frame_size], 'frames': records,
              'resized': False, 'per_frame_recentered': False, 'all_source_pixels_reconstruct': True,
              'distinct_frames': len({entry['sha256'] for entry in records}), 'visual_review': 'pending'}
    write_json(out / 'split-record.json', report)
    return report


def pack_frames(paths, out, frame_size=720, preview=False, duration_ms=350):
    need(len(paths) == 4, 'Exactly four frames are required in 1,2,3,4 order')
    need(type(frame_size) is int and frame_size > 0, 'Frame size must be positive')
    need(type(duration_ms) is int and duration_ms >= 10 and duration_ms % 10 == 0,
         'Preview duration must be a positive multiple of 10 milliseconds')
    out = new_output(out)
    frames = [rgba(path) for path in paths]
    need(all(im.size == (frame_size,frame_size) for im in frames), 'All four frames must match the final square canvas')
    strip = Image.new('RGBA', (frame_size*4,frame_size))
    for index, frame in enumerate(frames):
        strip.paste(frame,(index*frame_size,0))
    out.mkdir(parents=True)
    strip.save(out / 'body-4x1.png')
    report = {'workflow': 'body-keyframes', 'atlas': 'body-4x1.png', 'columns': 4, 'rows': 1,
              'frame_size': [frame_size,frame_size], 'frame_order': [1,2,3,4],
              'source_frames': [{'path': str(Path(p).resolve()), 'sha256': digest(p)} for p in paths],
              'runtime_binding': 'unbound', 'visual_review': 'pending',
              'note': 'Packing does not accept artwork, install a plugin or bind a runtime player.'}
    if preview:
        board = Image.new('RGB',(frame_size*2,frame_size*2),'white')
        rgb_frames = []
        side = min(frame_size,480)
        for index, frame in enumerate(frames):
            bg = Image.new('RGBA',frame.size,'white')
            bg.alpha_composite(frame)
            rendered = bg.convert('RGB')
            board.paste(rendered,((index%2)*frame_size,(index//2)*frame_size))
            rgb_frames.append(rendered.resize((side,side),Image.Resampling.LANCZOS))
        board.save(out / 'review-2x2.png')
        stack = Image.new('RGB',(side,side*4),'white')
        for index, frame in enumerate(rgb_frames):
            stack.paste(frame,(0,index*side))
        palette = stack.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
        quantized = [im.quantize(palette=palette,dither=Image.Dither.NONE) for im in rgb_frames]
        quantized[0].save(out/'preview.gif',save_all=True,append_images=quantized[1:],duration=duration_ms,
                          loop=0,disposal=2,optimize=False)
        report.update(preview='preview.gif',preview_duration_ms=duration_ms,
                      preview_note='Four existing keyframes only; white background, no interpolation.')
    write_json(out / 'pack-record.json',report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    p = sub.add_parser('plan');p.add_argument('--character',required=True);p.add_argument('--out',required=True)
    p.add_argument('--numbers',type=int,nargs='+');p.add_argument('--catalog');p.add_argument('--body-catalog')
    p = sub.add_parser('split');p.add_argument('--image',required=True);p.add_argument('--out',required=True)
    p.add_argument('--frame-size',type=int,default=720)
    p = sub.add_parser('pack');p.add_argument('--frames',required=True,nargs=4);p.add_argument('--out',required=True)
    p.add_argument('--frame-size',type=int,default=720);p.add_argument('--preview',action='store_true')
    p.add_argument('--duration-ms',type=int,default=350)
    args = parser.parse_args()
    try:
        if args.command == 'plan':
            result = plan(args.character,args.out,args.numbers,args.catalog,args.body_catalog)
        elif args.command == 'split':
            result = split_sheet(args.image,args.out,args.frame_size)
        else:
            result = pack_frames(args.frames,args.out,args.frame_size,args.preview,args.duration_ms)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError,TypeError) as error:
        parser.exit(1,f'ERROR: {error}\n')


if __name__ == '__main__':
    main()
