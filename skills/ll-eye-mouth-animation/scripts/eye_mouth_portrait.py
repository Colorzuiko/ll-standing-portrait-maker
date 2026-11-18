#!/usr/bin/env python3
"""Fixed-pose eye/mouth entry point; body actions are a separate workflow."""
import argparse
import json
import sys
from pathlib import Path


def prepare_args(argv):
    args = list(argv)
    if not args or args[0] in ('-h','--help'):
        return args
    if args[0] == 'plan':
        guard = argparse.ArgumentParser(add_help=False)
        guard.add_argument('--scope',choices=['face-only'],default='face-only')
        guard.parse_known_args(args[1:])
        args.extend(['--scope','face-only'])
    if args[0] == 'export' and not any(a in ('-h','--help') for a in args[1:]):
        guard = argparse.ArgumentParser(add_help=False)
        guard.add_argument('--manifest',required=True)
        parsed, _ = guard.parse_known_args(args[1:])
        manifest = json.loads(Path(parsed.manifest).read_text(encoding='utf-8'))
        if manifest.get('scope') != 'face-only' or manifest.get('motions') or any(
                item.get('mode') != 'reuse_default' for item in manifest.get('body_variants', [])):
            raise ValueError('Eye/mouth export requires a face-only plan without body motions; use the separate body workflow or the legacy combined exporter.')
    return args


def main(argv=None):
    try:
        args = prepare_args(sys.argv[1:] if argv is None else argv)
    except (ValueError,OSError,TypeError) as error:
        print(f'ERROR: {error}',file=sys.stderr)
        raise SystemExit(1)
    import ll_portrait_pipeline
    sys.argv = [sys.argv[0],*args]
    ll_portrait_pipeline.main()


if __name__ == '__main__':
    main()
