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

    def test_get_missing_dict(self):
        # No data already filled in
        with self.io:
            self.interface.do_command('get hello')
        self.assertEqual(self.interface.view.contents, [
            'msglog> get hello',
            'Failed to find key: \'hello\'',
        ])

    def test_get_untraversable(self):
        self.interface.data = { "hello": True }
        with self.io:
            self.interface.do_command('get hello world')
        self.assertEqual(self.interface.view.contents, [
            'msglog> get hello world',
            'Cannot inspect properties of object: True',
        ])

    def test_get_dict(self):
        self.interface.data['example'] = 'simple'
        with self.io:
            self.interface.do_command('get example')
        self.assertEqual(self.interface.view.contents, [
            'msglog> get example',
            '"simple"',
        ])

    def test_get_dict_multilayer(self):
        self.interface.data = {
            'example': {
                'inside that' : 'creamy filling'
            }
        }
        with self.io:
            self.interface.do_command('get example "inside that"')
        self.assertEqual(self.interface.view.contents, [
            'msglog> get example "inside that"',
            '"creamy filling"',
        ])

    def test_get_array_missing(self):
        self.interface.data = {
            'example': []
        }
        with self.io:
            self.interface.do_command('get example 0')
        self.assertEqual(self.interface.view.contents, [
            'msglog> get example 0',
            'Failed to find key: 0',
        ])

    def test_get_array(self):
        self.interface.data = {
            'example': [
                'this',
                'that',
            ]
        }
        with self.io:
            self.interface.do_command('get example 1')
        self.assertEqual(self.interface.view.contents, [
            'msglog> get example 1',
            '"that"',
        ])

    def test_get_complex(self):
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
            self.interface.do_command('get example')
        self.assertEqual(self.interface.view.contents, [
            'msglog> get example',
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

    def test_set_bad_traversal(self):
        with self.io:
            self.interface.do_command('set a b c 0')
        self.assertEqual(self.interface.view.contents, [
            'msglog> set a b c 0',
            'Failed to find key: \'a\'',
        ])

    def test_set_untraversable(self):
        self.interface.data = { "hello": True }
        with self.io:
            self.interface.do_command('set hello world 0')
        self.assertEqual(self.interface.view.contents, [
            'msglog> set hello world 0',
            'Cannot inspect properties of object: True',
        ])

    def test_set_simple(self):
        with self.io:
            self.interface.do_command('set a {}')
        self.assertEqual(self.interface.view.contents, [
            'msglog> set a {}',
        ])
        self.assertEqual(
            self.interface.data,
            { 'a': {} }
        )

    def test_set_complex(self):
        cmd = 'set a \'[4, true, null, {"no":false}]\''
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

    def test_set_bad_json(self):
        cmd = 'set hello world'
        with self.io:
            self.interface.do_command(cmd)
        self.assertEqual(self.interface.view.contents, [
            'msglog> ' + cmd,
            'Could not decode last parameter as JSON.',
        ])

    def test_set_multi_traversal(self):
        with self.io:
            self.interface.do_command('set a {}')
            self.interface.do_command('set a b 3')
        self.assertEqual(self.interface.view.contents, [
            'msglog> set a {}',
            'msglog> set a b 3',
        ])
        self.assertEqual(
            self.interface.data,
            {
                'a': { 'b': 3 }
            }
        )

    def test_set_root(self):
        with self.io:
            self.interface.do_command('set \'{"hello":"world"}\'')
        self.assertEqual(self.interface.view.contents, [
            'msglog> set \'{"hello":"world"}\'',
        ])
        self.assertEqual(
            self.interface.data,
            {
                'hello':'world'
            }
        )
