#!/usr/bin/env python3
"""Render the repository's generic package glyph; never replace an original icon.

Only the Python standard library is used, so Linux CI and macOS produce identical
PNG files. These are deliberately recorded as fallbacks in config/packages.json.
"""
import json
import math
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parent.parent


def render(color):
    size, scale = 128, 2
    rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
    edges = [((32, 45), (64, 28)), ((64, 28), (96, 45)),
             ((96, 45), (64, 62)), ((64, 62), (32, 45)),
             ((32, 45), (32, 82)), ((32, 82), (64, 100)),
             ((64, 100), (96, 82)), ((96, 82), (96, 45)),
             ((64, 62), (64, 100)), ((49, 37), (80, 54))]

    def distance(x, y, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        t = max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy)))
        return math.hypot(x - a[0] - t * dx, y - a[1] - t * dy)

    pixels = bytearray()
    for y in range(size):
        pixels.append(0)
        for x in range(size):
            samples = []
            for sy in range(scale):
                for sx in range(scale):
                    xx, yy = x + (sx + .5) / scale, y + (sy + .5) / scale
                    corner = math.hypot(max(24 - xx, 0, xx - 104), max(24 - yy, 0, yy - 104))
                    if corner > 24:
                        samples.append((0, 0, 0, 0))
                    elif min(distance(xx, yy, *line) for line in edges) < 2.25:
                        samples.append((250, 253, 255, 255))
                    else:
                        lift = int(22 * (1 - yy / size))
                        samples.append(tuple(min(255, v + lift) for v in rgb) + (255,))
            pixels.extend(round(sum(s[c] for s in samples) / len(samples)) for c in range(4))

    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', size, size, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(pixels), 9)) + chunk(b'IEND', b''))


if __name__ == '__main__':
    cache = {}
    for package in json.loads((ROOT / 'config/packages.json').read_text()).values():
        icon = package['icon']
        if icon['kind'] == 'repository-fallback':
            if icon['color'] not in cache:
                cache[icon['color']] = render(icon['color'])
            (ROOT / icon['path']).write_bytes(cache[icon['color']])
    print('已生成目录中登记的通用图标；插件原图标保持不变。')
