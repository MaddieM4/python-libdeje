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

import json
import os.path
from deje.tests.dexter_commands import DexterCommandTester, Tempfile

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

    def test_vdel_root(self):
        self.interface.data = { "hello": True }
        with self.io:
            self.interface.do_command('vdel')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vdel',
        ])
        self.assertEqual(self.interface.data, {})

    def test_vdel_single(self):
        self.interface.data = { "hello": True, "world": False }
        with self.io:
            self.interface.do_command('vdel hello')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vdel hello',
        ])
        self.assertEqual(self.interface.data, { "world": False })

    def test_vdel_deep(self):
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
            self.interface.do_command('vdel example 2 maybe')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vdel example 2 maybe',
        ])
        self.assertEqual(self.interface.data, {
            'example': [
                'this',
                'that',
                {
                    'yes'   : True,
                    'no'    : False,
                    'number': -29,
                }
            ]
        })
        with self.io:
            self.interface.do_command('vdel example 2')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vdel example 2 maybe',
            'msglog> vdel example 2',
        ])
        self.assertEqual(self.interface.data, {
            'example': [
                'this',
                'that',
            ]
        })

    def test_vdel_missing(self):
        self.interface.data = { "hello": True }
        with self.io:
            self.interface.do_command('vdel beans')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vdel beans',
            'Failed to find key: \'beans\'',
        ])
        self.assertEqual(self.interface.data, { "hello": True })

    def test_vdel_untraversable(self):
        self.interface.data = { "hello": True }
        with self.io:
            self.interface.do_command('vdel hello farmer')
        self.assertEqual(self.interface.view.contents, [
            'msglog> vdel hello farmer',
            'Cannot inspect properties of object: True',
        ])
        self.assertEqual(self.interface.data, { "hello": True })

    def test_vsave_root(self):
        self.interface.data = {
            'hello': 'world',
            'numbers': [8,9,10,11,12],
        }
        with Tempfile() as fname:
            cmd = 'vsave ' + fname
            with self.io:
                self.interface.do_command(cmd)
            self.assertEqual(self.interface.view.contents, [
                'msglog> ' + cmd,
            ])
            self.assertEqual(
                json.load(open(fname)),
                self.interface.data
            )

    def test_vsave_subset(self):
        self.interface.data = {
            'hello': 'world',
            'numbers': [8,9,10,11,12],
        }
        with Tempfile() as fname:
            cmd = 'vsave %s numbers' % fname
            with self.io:
                self.interface.do_command(cmd)
            self.assertEqual(self.interface.view.contents, [
                'msglog> ' + cmd,
            ])
            self.assertEqual(
                json.load(open(fname)),
                self.interface.data['numbers']
            )

    def test_vsave_bad_traversal(self):
        self.interface.data = {
            'hello': 'world',
            'numbers': [8,9,10,11,12],
        }
        with Tempfile() as fname:
            cmd = 'vsave %s this_key_does_not_exist' % fname
            with self.io:
                self.interface.do_command(cmd)
            self.assertEqual(self.interface.view.contents, [
                'msglog> ' + cmd,
                'Failed to find key: \'this_key_does_not_exist\'',
            ])
            self.assertEqual(open(fname).read(), '')

    def test_vload_root(self):
        original = {
            'hello': 'world',
            'numbers': [8,9,10,11,12],
        }
        self.interface.data = original

        with Tempfile() as fname:
            with self.io:
                self.interface.do_command('vsave ' + fname)
                self.interface.data = {}
                self.interface.do_command('vload ' + fname)
            self.assertEqual(self.interface.view.contents, [
                'msglog> vsave ' + fname,
                'msglog> vload ' + fname,
            ])
            self.assertEqual(
                original,
                self.interface.data
            )

    def test_vload_subset(self):
        self.interface.data = {
            'hello': 'world',
            'numbers': [8,9,10,11,12],
        }
        with Tempfile() as fname:
            with self.io:
                self.interface.do_command('vsave %s numbers' % fname)
                self.interface.data = {}
                self.interface.do_command('vload %s numbers' % fname)
            self.assertEqual(self.interface.view.contents, [
                'msglog> vsave %s numbers' % fname,
                'msglog> vload %s numbers' % fname,
            ])
            self.assertEqual(
                { 'numbers': [8,9,10,11,12] },
                self.interface.data
            )

    def test_vload_no_such_file(self):
        original = {
            'hello': 'world',
            'numbers': [8,9,10,11,12],
        }
        self.interface.data = original

        cmd = 'vload this_file_does_not_exist'
        with self.io:
            self.interface.do_command(cmd)
        self.assertEqual(self.interface.view.contents, [
            'msglog> ' + cmd,
            'IOError 2: No such file or directory',
        ])
        self.assertEqual(
            original,
            self.interface.data
        )
