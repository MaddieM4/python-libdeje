'''
This file is part of python-libdeje.

python-libdeje is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python-libdeje is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with python-libdeje.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import absolute_import

from deje.tests.dexter_commands import DexterCommandTester

class TestDexterVarsGroup(DexterCommandTester):

    def test_vget_missing_dict(self):
        # No data already filled in
        with self.io:
            self.interface.do_command('vget hello')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vget hello',
            'Failed to find key: \'hello\'',
        ])

    def test_vget_untraversable(self):
        self.interface.data = { "hello": True }
        with self.io:
            self.interface.do_command('vget hello world')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vget hello world',
            'Cannot inspect properties of object: True',
        ])

    def test_vget_dict(self):
        self.interface.data['example'] = 'simple'
        with self.io:
            self.interface.do_command('vget example')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vget example',
            '"simple"',
        ])

    def test_vget_dict_multilayer(self):
        self.interface.data = {
            'example': {
                'inside that' : 'creamy filling'
            }
        }
        with self.io:
            self.interface.do_command('vget example "inside that"')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vget example "inside that"',
            '"creamy filling"',
        ])

    def test_vget_array_missing(self):
        self.interface.data = {
            'example': []
        }
        with self.io:
            self.interface.do_command('vget example 0')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vget example 0',
            'Failed to find key: 0',
        ])

    def test_vget_array(self):
        self.interface.data = {
            'example': [
                'this',
                'that',
            ]
        }
        with self.io:
            self.interface.do_command('vget example 1')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vget example 1',
            '"that"',
        ])

    def test_vget_complex(self):
        self.interface.data = {
            'example': [
                'this',
                'that',
                {
                    'yes'   : True,
                    'no'    : False,
                    'maybe' : None,
                    'number': -29,
                }
            ]
        }
        with self.io:
            self.interface.do_command('vget example')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vget example',
            '[',
            '  "this", ',
            '  "that", ',
            '  {',
            '    "maybe": null, ',
            '    "no": false, ',
            '    "number": -29, ',
            '    "yes": true',
            '  }',
            ']',
        ])

    def test_vset_bad_traversal(self):
        with self.io:
            self.interface.do_command('vset a b c 0')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vset a b c 0',
            'Failed to find key: \'a\'',
        ])

    def test_vset_untraversable(self):
        self.interface.data = { "hello": True }
        with self.io:
            self.interface.do_command('vset hello world 0')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vset hello world 0',
            'Cannot inspect properties of object: True',
        ])

    def test_vset_simple(self):
        with self.io:
            self.interface.do_command('vset a {}')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vset a {}',
        ])
        self.assertEqual(
            self.interface.data,
            { 'a': {} }
        )

    def test_vset_complex(self):
        cmd = 'vset a \'[4, true, null, {"no":false}]\''
        with self.io:
            self.interface.do_command(cmd)
        self.assertEqual(self.interface.view.contents, [
            'msglog> ' + cmd,
        ])
        self.assertEqual(
            self.interface.data,
            {
                'a': [
                    4, True, None, { "no": False }
                ]
            }
        )

    def test_vset_bad_json(self):
        cmd = 'vset hello world'
        with self.io:
            self.interface.do_command(cmd)
        self.assertEqual(self.interface.view.contents, [
            'msglog> ' + cmd,
            'Could not decode last parameter as JSON.',
        ])

    def test_vset_multi_traversal(self):
        with self.io:
            self.interface.do_command('vset a {}')
            self.interface.do_command('vset a b 3')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vset a {}',
            'msglog> vset a b 3',
        ])
        self.assertEqual(
            self.interface.data,
            {
                'a': { 'b': 3 }
            }
        )

    def test_vset_root(self):
        with self.io:
            self.interface.do_command('vset \'{"hello":"world"}\'')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vset \'{"hello":"world"}\'',
        ])
        self.assertEqual(
            self.interface.data,
            {
                'hello':'world'
            }
        )