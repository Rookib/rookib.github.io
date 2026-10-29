#!/usr/bin/env python3
"""Generate localized APT overrides and static web depictions; validate the pool.

The .deb files are read only. Package IDs, versions, dependencies, architectures,
licenses and executable payloads are not rewritten by this script.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys

from deb_archive import control, parse_control

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://rookib.github.io/'
DISPLAY_FIELDS = {'Name', 'Description', 'Section', 'Author', 'Maintainer',
                  'Icon', 'Depiction', 'SileoDepiction'}


def inline(text):
    escaped = html.escape(text)
    escaped = re.sub(r'`([^`]+)`', r'<code>\1</code>', escaped)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', escaped)


def markdown(text):
    blocks = []
    for paragraph in text.split('\n\n'):
        if paragraph.startswith('- '):
            blocks.append('<ul>' + ''.join('<li>' + inline(line[2:]) + '</li>'
                          for line in paragraph.splitlines() if line.startswith('- ')) + '</ul>')
        else:
            blocks.append('<p>' + inline(paragraph).replace('\n', '<br>') + '</p>')
    return '\n'.join(blocks)


def page(package, depiction):
    title = html.escape(package['name'])
    content = []
    for tab in depiction['tabs']:
        content.append('<section><h2>' + html.escape(tab['tabname']) + '</h2>')
        for view in tab['views']:
            kind = view['class']
            if kind in ('DepictionHeaderView', 'DepictionSubheaderView'):
                content.append('<h3>' + html.escape(view['title']) + '</h3>')
            elif kind == 'DepictionMarkdownView':
                content.append(markdown(view['markdown']))
            elif kind == 'DepictionTableTextView':
                content.append('<p class="row"><span>' + html.escape(view['title']) +
                               '</span><strong>' + html.escape(view['text']) + '</strong></p>')
            elif kind == 'DepictionSeparatorView':
                content.append('<hr>')
            else:
                raise ValueError(f'Unsupported web depiction class: {kind}')
        content.append('</section>')
    return ('<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{title} · Hello Rookib</title>'
            '<link rel="stylesheet" href="../../assets/depiction.css"></head><body><main>'
            '<nav><a href="../../">← Hello Rookib 软件源</a></nav><header>'
            f'<img src="../../{package["icon"]["path"]}" width="72" height="72" alt="">'
            f'<div><h1>{title}</h1><p>作者：Rookib</p></div></header>'
            + '\n'.join(content) +
            '<footer>源内展示作者统一为 Rookib；原始许可与版权声明保留在软件包及源码中。</footer>'
            '</main></body></html>\n')


def write_or_check(path, text, check):
    if check:
        if not path.is_file() or path.read_text() != text:
            raise ValueError(f'Generated file is stale: {path.relative_to(ROOT)}; run scripts/build-metadata.py')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def inspect_pool(catalog):
    entries, identities = [], set()
    for path in sorted((ROOT / 'pool').glob('*.deb')):
        fields = control(path)
        identity = tuple(fields[k] for k in ('Package', 'Version', 'Architecture'))
        if identity in identities:
            raise ValueError(f'Duplicate package/version/architecture: {identity}')
        if fields['Package'] not in catalog:
            raise ValueError(f'Package lacks Chinese metadata: {fields["Package"]}')
        identities.add(identity)
        entries.append((path, fields))
    return entries


def validate_index(path, entries, catalog):
    records = [parse_control(record) for record in path.read_text().strip().split('\n\n') if record]
    expected = {tuple(c[k] for k in ('Package', 'Version', 'Architecture')): (p, c) for p, c in entries}
    seen = set()
    for record in records:
        # Debian field names are case-insensitive. dpkg serializes the custom
        # SileoDepiction field as Sileodepiction; values remain case-sensitive.
        normalized = {key.casefold(): value for key, value in record.items()}
        if len(normalized) != len(record):
            raise ValueError('Duplicate index field with different capitalization')
        record = normalized
        identity = tuple(record[k.casefold()] for k in ('Package', 'Version', 'Architecture'))
        if identity in seen or identity not in expected:
            raise ValueError(f'Unexpected or duplicate index entry: {identity}')
        seen.add(identity)
        deb, original = expected[identity]
        for key, value in original.items():
            # Size in a package control file may be stale after repacking.
            # Validate the index size against the actual archive below instead.
            if key.casefold() not in {k.casefold() for k in DISPLAY_FIELDS | {'Size'}} and record.get(key.casefold()) != value:
                raise ValueError(f'Index changed {key}: {identity}')
        if record.get('sha256') != hashlib.sha256(deb.read_bytes()).hexdigest():
            raise ValueError(f'Wrong package hash: {identity}')
        if record.get('filename') != 'pool/' + deb.name or record.get('size') != str(deb.stat().st_size):
            raise ValueError(f'Wrong package location/size: {identity}')
        for key, value in overrides(catalog[identity[0]], identity[0]).items():
            if record.get(key.casefold()) != value:
                raise ValueError(f'Wrong display field {key}: {identity}')
    if seen != set(expected):
        raise ValueError(f'APT index dropped package versions/architectures: {set(expected) - seen}')


def overrides(package, pid):
    return {'Name': package['name'], 'Description': package['description'],
            'Section': package['section'], 'Author': package['author'], 'Maintainer': 'Rookib',
            'Icon': BASE + package['icon']['path'], 'Depiction': BASE + 'depictions/' + pid + '/',
            'SileoDepiction': BASE + 'depictions/' + pid + '.json'}


def package_listing(catalog):
    cards = []
    for pid, package in catalog.items():
        cards.append(f'<a class="package-card" href="depictions/{pid}/">'
                     f'<img src="{package["icon"]["path"]}" width="56" height="56" alt="">'
                     f'<div><h2>{html.escape(package["name"])}</h2>'
                     f'<p>{html.escape(package["description"])}</p><small>Rookib · '
                     f'{html.escape(package["section"])}</small></div></a>')
    return ('<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>插件目录 · Hello Rookib</title><link rel="stylesheet" href="assets/depiction.css">'
            '</head><body><main><nav><a href="./">← Hello Rookib 软件源</a></nav>'
            '<header><img src="assets/avatar.png?v=42058af9debc" width="72" height="72" alt="Hello Rookib 源头像">'
            '<div><h1>插件目录</h1><p>中文详情 · Hello Rookib</p></div></header>'
            + '\n'.join(cards) + '</main></body></html>\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate without writing generated files')
    parser.add_argument('--check-index', type=Path, help='Also validate a built Packages index')
    parser.add_argument('--require-versions', action='store_true', help='Require every advertised version in pool')
    args = parser.parse_args()
    catalog = json.loads((ROOT / 'config/packages.json').read_text())
    entries = inspect_pool(catalog)
    lines = []
    for pid, package in sorted(catalog.items()):
        if not re.fullmatch(r'[A-Za-z0-9.+-]+', pid):
            raise ValueError(f'Unsafe package ID: {pid}')
        if package['author'] != 'Rookib' or not re.search('[\u4e00-\u9fff]', package['description']):
            raise ValueError(f'Missing Rookib/Chinese display metadata: {pid}')
        icon = ROOT / package['icon']['path']
        if not icon.is_relative_to(ROOT / 'assets/packages') or not icon.is_file():
            raise ValueError(f'Missing package icon: {pid}')
        data = icon.read_bytes()
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError(f'Icon must be PNG: {pid}')
        recorded = package['icon'].get('sha256')
        if recorded and recorded != hashlib.sha256(data).hexdigest():
            raise ValueError(f'Original icon bytes changed: {pid}')
        depiction = json.loads((ROOT / 'depictions' / (pid + '.json')).read_text())
        views = depiction['tabs'][0]['views']
        if not any(v.get('title') == '作者' and v.get('text') == 'Rookib' for v in views):
            raise ValueError(f'Depiction missing author: {pid}')
        if args.require_versions:
            versions = {c['Version'] for _, c in entries if c['Package'] == pid}
            latest = next(v['text'] for v in views if v.get('title') == '当前版本')
            if latest not in versions:
                raise ValueError(f'Advertised version not present in pool: {pid} {latest}')
        for key, value in overrides(package, pid).items():
            if '\n' in value or '\r' in value:
                raise ValueError(f'Multiline APT override: {pid} {key}')
            lines.append(f'{pid} {key} {value}\n')
        write_or_check(ROOT / 'depictions' / pid / 'index.html', page(package, depiction), args.check)
    write_or_check(ROOT / 'config/package-overrides', ''.join(lines), args.check)
    write_or_check(ROOT / 'packages.html', package_listing(catalog), args.check)
    if args.check_index:
        validate_index(args.check_index, entries, catalog)
    print(f'已验证 {len(catalog)} 个插件的中文详情与图标、{len(entries)} 个安装包。')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        sys.exit(str(error))
