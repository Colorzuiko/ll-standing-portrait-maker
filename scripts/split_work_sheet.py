#!/usr/bin/env python3
"""Split four equal frames: horizontal combined-face/body work, or vertical atlases."""
import argparse
import json
from pathlib import Path
from PIL import Image


def split_sheet(image, width, height, out, columns=1):
    out = Path(out)
    if out.exists():
        raise ValueError('Output exists; choose a new directory')
    if columns not in (1,4):
        raise ValueError('Use 4 columns for horizontal work strips, or 1 column for vertical atlases')
    with Image.open(image) as sheet:
        expected=(width*columns,height*(4//columns))
        if sheet.format != 'PNG' or sheet.mode != 'RGBA' or sheet.size != expected:
            layout='one column and four rows' if columns==1 else 'four columns and one row'
            raise ValueError(f'Expected RGBA PNG {expected[0]}x{expected[1]}, {layout}')
        frames = [sheet.crop(((i%columns)*width,(i//columns)*height,(i%columns+1)*width,(i//columns+1)*height)) for i in range(4)]
    out.mkdir(parents=True)
    for i, frame in enumerate(frames):
        frame.save(out / f'frame_{i}.png')
    return {'frames': [str(out / f'frame_{i}.png') for i in range(4)], 'frame_size': [width, height], 'columns':columns}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', required=True)
    parser.add_argument('--width', type=int, default=720)
    parser.add_argument('--height', type=int, default=720)
    parser.add_argument('--out', required=True)
    parser.add_argument('--columns',type=int,choices=[1,4],default=1)
    args = parser.parse_args()
    if args.width < 1 or args.height < 1:
        parser.error('Width and height must be positive')
    try:
        print(json.dumps(split_sheet(args.image, args.width, args.height, args.out,args.columns), indent=2))
    except (ValueError, OSError) as error:
        parser.exit(1, str(error)+'\n')
