#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Print the images of a WIM or ESD file as JSON, and which of them are wanted.

    wim_images.py <install.wim|-> [wanted ...]

'-' reads the file from standard input (7z e -so <iso> sources/install.wim), so
an ISO can be inspected without extracting it. A wanted entry matches an image
by index, name or edition ID, case-insensitively; with no entry every image is
wanted. Output: {"images": [{index, name, edition_id, build, sp_build, arch,
languages}], "keep": [indexes], "lines": [one readable line per image]}.

The XML resource of a WIM names its images; the header says where it is. It is
stored uncompressed, also in ESD files.
"""
import json
import struct
import sys
import xml.etree.ElementTree as ET

MAGIC = b'MSWIM\0\0\0'


def read_xml(stream):
    head = stream.read(0xD0)
    if head[:8] != MAGIC:
        raise SystemExit('not a WIM file')
    size = int.from_bytes(head[0x48:0x4F], 'little')
    offset = struct.unpack_from('<Q', head, 0x50)[0]
    if stream.seekable():
        stream.seek(offset)
    else:
        left = offset - len(head)
        while left > 0:
            chunk = stream.read(min(left, 1 << 20))
            if not chunk:
                raise SystemExit('file ends before its XML resource')
            left -= len(chunk)
    data = stream.read(size)
    return ET.fromstring(data.decode('utf-16').lstrip('﻿'))


def images(root):
    found = []
    for image in root.iter('IMAGE'):
        found.append({
            'index': int(image.get('INDEX')),
            'name': image.findtext('NAME') or '',
            'edition_id': image.findtext('WINDOWS/EDITIONID') or '',
            'build': int(image.findtext('WINDOWS/VERSION/BUILD') or 0),
            'sp_build': int(image.findtext('WINDOWS/VERSION/SPBUILD') or 0),
            'arch': int(image.findtext('WINDOWS/ARCH') or -1),
            'languages': [x.text for x in image.findall('WINDOWS/LANGUAGES/LANGUAGE')],
        })
    return sorted(found, key=lambda i: i['index'])


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    if argv[1] == '-':
        root = read_xml(sys.stdin.buffer)
    else:
        with open(argv[1], 'rb') as f:
            root = read_xml(f)
    found = images(root)
    wanted = {w.strip().lower() for w in argv[2:] if w.strip()}
    keep = [i['index'] for i in found
            if not wanted
            or str(i['index']) in wanted
            or i['name'].lower() in wanted
            or i['edition_id'].lower() in wanted]
    lines = [f"{i['index']}: {i['name']} ({i['edition_id']}, {i['build']}.{i['sp_build']})"
             for i in found]
    json.dump({'images': found, 'keep': keep, 'lines': lines}, sys.stdout)


if __name__ == '__main__':
    main(sys.argv)
