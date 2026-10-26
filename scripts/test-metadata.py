#!/usr/bin/env python3
"""Regression checks for Debian field names and archive size validation."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('metadata', Path(__file__).with_name('build-metadata.py'))
metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata)


class IndexFields(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.deb = root / 'example.deb'
        self.deb.write_bytes(b'unchanged payload')
        self.index = root / 'Packages'
        self.control = {'Package': 'example', 'Version': '1.0',
                        'Architecture': 'iphoneos-arm64e', 'Depends': 'firmware (>= 16.0)'}
        self.catalog = {'example': {'name': '示例', 'description': '中文说明',
                                   'author': 'Rookib', 'section': '工具',
                                   'icon': {'path': 'assets/packages/example.png'}}}
        self.fields = dict(self.control, Filename='pool/example.deb', Size='17',
                           SHA256=hashlib.sha256(self.deb.read_bytes()).hexdigest())
        self.fields.update(metadata.overrides(self.catalog['example'], 'example'))

    def validate(self, fields):
        self.index.write_text(''.join(f'{k}: {v}\n' for k, v in fields.items()) + '\n')
        metadata.validate_index(self.index, [(self.deb, self.control)], self.catalog)

    def test_dpkg_custom_field_capitalization(self):
        self.fields['Sileodepiction'] = self.fields.pop('SileoDepiction')
        self.validate(self.fields)

    def test_all_field_names_case_insensitive(self):
        self.validate({k.lower(): v for k, v in self.fields.items()})

    def test_url_values_remain_case_sensitive(self):
        self.fields['SileoDepiction'] = self.fields['SileoDepiction'].upper()
        with self.assertRaisesRegex(ValueError, 'Wrong display field'):
            self.validate(self.fields)

    def test_dependency_changes_still_fail(self):
        self.fields['Depends'] = 'firmware (>= 17.0)'
        with self.assertRaisesRegex(ValueError, 'Index changed Depends'):
            self.validate(self.fields)

    def test_stale_control_size_uses_actual_archive_size(self):
        self.control['Size'] = '999999'
        self.validate(self.fields)

    def test_matching_control_size_cannot_mask_wrong_index_size(self):
        self.control['Size'] = '999999'
        self.fields['Size'] = '999999'
        with self.assertRaisesRegex(ValueError, 'Wrong package location/size'):
            self.validate(self.fields)

    def test_duplicate_capitalizations_fail(self):
        self.fields['Sileodepiction'] = self.fields['SileoDepiction']
        with self.assertRaisesRegex(ValueError, 'Duplicate index field'):
            self.validate(self.fields)


if __name__ == '__main__':
    unittest.main()
