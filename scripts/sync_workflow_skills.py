#!/usr/bin/env python3
"""Sync canonical shared resources into two standalone skills; optionally package them."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BODY = 'll-body-keyframes'
EYE = 'll-eye-mouth-animation'
COMMON_CATALOGS = [
    'references/expression-catalog-60.md',
    'references/body-language-catalog-60.md',
    'references/body-language-catalog-60-v2.md',
    'references/expression-catalog-60-body-v2.json',
    'references/emontion-audit-52.md',
]
SOURCES = {
    BODY: ['requirements.txt', 'scripts/body_keyframes.py', 'scripts/catalogs.py', *COMMON_CATALOGS],
    EYE: ['requirements.txt', 'scripts/eye_mouth_portrait.py', 'scripts/ll_portrait_pipeline.py',
          'scripts/catalogs.py', 'scripts/shared_export.py', 'scripts/shared_report.py',
          'scripts/split_work_sheet.py', *COMMON_CATALOGS,
          'references/expression-coordination.md', 'references/style-and-layout.md',
          'references/layers-and-qa.md', 'references/eye-mouth-sharing.md',
          'references/manifest-and-export.md', 'references/plugin-contract.md',
          'assets/LL_StandingPictureDirect.js', 'assets/report.html', 'assets/body-report.html'],
}
OWNED = {
    BODY: ['SKILL.md', 'agents/openai.yaml', 'references/body-style-and-layout.md',
           'references/layered-body-variant.md', 'references/body-keyframe-tools.md'],
    EYE: ['SKILL.md', 'agents/openai.yaml'],
}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def synchronize(check=False, root=ROOT):
    expected = []
    for name, paths in SOURCES.items():
        records = []
        for relative in paths:
            data = (root / relative).read_bytes()
            expected.append((root / 'skills' / name / relative, data))
            records.append({'source': relative, 'target': relative, 'sha256': sha(data)})
        index = {'schema_version': 1, 'skill': name, 'canonical_source': 'repository root',
                 'refresh_command': 'python -X utf8 scripts/sync_workflow_skills.py', 'files': records}
        expected.append((root / 'skills' / name / 'bundle-sources.json', encoded(index)))
    stale = [path.relative_to(root).as_posix() for path, data in expected
             if not path.is_file() or path.read_bytes() != data]
    if check and stale:
        raise ValueError('Standalone resources need syncing: ' + ', '.join(stale))
    if not check:
        for path, data in expected:
            if not path.is_file() or path.read_bytes() != data:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
    return {'mode': 'check' if check else 'sync', 'shared_files': len(expected),
            'updated': [] if check else stale, 'status': 'passed'}


def package(out, root=ROOT):
    synchronize(check=True, root=root)
    out = Path(out).resolve()
    if out.exists():
        raise ValueError('Package output exists; choose a new directory')
    # An explicit allowlist keeps generated art, caches and user output out of skill ZIPs.
    files = {name: sorted(set([*paths, *OWNED[name], 'bundle-sources.json']))
             for name, paths in SOURCES.items()}
    for name, paths in files.items():
        for relative in paths:
            if not (root / 'skills' / name / relative).is_file():
                raise ValueError(f'Missing skill file: {name}/{relative}')
    out.mkdir(parents=True)
    records = []
    for name, paths in files.items():
        target = out / f'{name}.zip'
        with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for relative in paths:
                archive.write(root / 'skills' / name / relative, f'{name}/{relative}')
        records.append({'skill': name, 'file': target.name, 'files': len(paths),
                        'bytes': target.stat().st_size, 'sha256': sha(target.read_bytes())})
    report = {'schema_version': 1, 'packages': records, 'globally_installed': False}
    (out / 'packages.json').write_bytes(encoded(report))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if shared copies are stale; no writes')
    parser.add_argument('--package', metavar='NEW_OUT', help='Package synced standalone skills into new ZIPs')
    args = parser.parse_args()
    try:
        result = package(args.package) if args.package else synchronize(check=args.check)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        parser.exit(1, f'ERROR: {error}\n')


if __name__ == '__main__':
    main()
