"""Read the authoritative facial/body Markdown catalogs; JSON is an explicit override only."""
import hashlib
import json
import re
from pathlib import Path

REFERENCES = Path(__file__).resolve().parents[1] / 'references'


def rows(path):
    result = []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if re.match(r'^\|\s*\d{2}\s*\|', line):
            cells = [part.strip() for part in line.strip().strip('|').split('|')]
            result.append(cells)
    if not result or len({int(r[0]) for r in result}) != len(result):
        raise ValueError(f'Empty catalog or duplicate numbers: {path}')
    return result


def load_catalog(catalog=None, body_catalog=None):
    face_path = Path(catalog) if catalog else REFERENCES / 'expression-catalog-60.md'
    provenance = {'face_path': str(face_path.resolve()),
                  'face_sha256': hashlib.sha256(face_path.read_bytes()).hexdigest(),
                  'authority': 'explicit-user-catalog' if catalog else 'SKILL_3RD canonical Markdown'}
    if face_path.suffix.lower() == '.json':
        items = json.loads(face_path.read_text(encoding='utf-8'))
        if not isinstance(items, list):
            raise ValueError('Catalog JSON must be a list')
    else:
        items = []
        for no, name, english, prompt in rows(face_path):
            slug = re.sub(r'[^a-z0-9]+', '_', english.lower()).strip('_')
            items.append({'no': int(no), 'id': f'{int(no):02}_{slug}', 'name': name,
                          'english': english, 'face': prompt, 'rest_eyes': 'expression',
                          'rest_mouth': 'expression'})
        # Preserve special resting eyes; a generic bilateral blink would erase their meaning.
        if catalog is None:
            for item in items:
                if item['no'] in (9, 22, 28, 38, 43, 57, 58, 59):
                    item['eye_auto'] = False
                if item['no'] in (53, 60):
                    item.update(rest_eyes='open', eye_auto=True, eye_motion={
                        'type': 'single_eye_wink',
                        'moving_eye': 'reference_selected',
                        'other_eye': 'open',
                        'frame_states': [
                            {'moving_eye': state, 'other_eye': 'open'}
                            for state in ('open', 'half_closed', 'closed', 'half_open')
                        ]})
                if item['no'] == 60:
                    item.update(rest_mouth='closed', mouth_motion={
                        'type': 'tongue_extension',
                        'frame_states': ['closed', 'tongue_tip', 'tongue_partial', 'tongue_longest']})
    body_path = Path(body_catalog) if body_catalog else (
        REFERENCES / 'body-language-catalog-60.md' if catalog is None else None)
    if body_path:
        body = {int(r[0]): r for r in rows(body_path)}
        if set(body) != {int(item.get('no', i)) for i, item in enumerate(items, 1)}:
            raise ValueError('Facial and body catalog numbers differ')
        for i, item in enumerate(items, 1):
            row = body[int(item.get('no', i))]
            if item['name'] != row[1] or row[2] not in ('new_pose', 'reuse_default'):
                raise ValueError(f'Facial/body catalog mismatch at {row[0]}')
            item.update(body_mode=row[2], body_hint=row[3], body_prompt=row[4])
        provenance.update(body_path=str(body_path.resolve()),
                          body_sha256=hashlib.sha256(body_path.read_bytes()).hexdigest())
    if catalog is None and [item['no'] for item in items] != list(range(1, 61)):
        raise ValueError('Canonical catalog must contain numbers 01–60 in order')
    return items, provenance
