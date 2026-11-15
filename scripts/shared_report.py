"""Render an offline layered preview against the exported runtime files."""
import json
from pathlib import Path


def render_report(folder, result, configs, canvas, preview):
    data = {'result': result, 'configs': configs, 'canvas': canvas, 'preview': preview}
    template = (Path(__file__).resolve().parents[1] / 'assets/report.html').read_text(encoding='utf-8')
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    (folder / 'report.html').write_text(template.replace('__DATA__', payload), encoding='utf-8')
    render_body_report(folder, result)


def render_body_report(folder, result):
    items = {item['id']: item for item in result['items']}
    motions = []
    for motion in result.get('motions', []):
        item = items[motion['expression_id']]
        motions.append({'no': item['no'], 'name': item['name'],
                        'hint': item['body'].get('body_hint', ''),
                        'image': motion['image'],
                        'frameWait': motion['frame_duration']})
    data = {'character': result.get('character_name', result['character_id']),
            'art_complete': result['art_complete'],
            'engine_verification': result.get('engine_verification', 'not_run'),
            'motions': sorted(motions, key=lambda row: row['no']),
            'reuse': [{'no': item['no'], 'name': item['name']}
                      for item in result['items']
                      if item['status'] == 'exported' and item['body']['mode'] == 'reuse_default']}
    template = (Path(__file__).resolve().parents[1] / 'assets/body-report.html').read_text(encoding='utf-8')
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    (Path(folder) / 'body-report.html').write_text(template.replace('__BODY_DATA__', payload), encoding='utf-8')
