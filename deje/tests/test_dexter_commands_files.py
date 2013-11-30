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

import os
import tempfile

from deje.tests.dexter_commands import DexterCommandTester

class TestDexterBasicGroup(DexterCommandTester):

    def test_fwrite_current_view(self):
        _, fname = tempfile.mkstemp()
        try:
            with self.io:
                self.interface.do_command('view cows')
                self.interface.do_command('notacommand')
                self.interface.do_command('fwrite '+ fname)
            written = open(fname, 'r').read()
            self.assertEqual(written.split('\n'), [
                'cows> notacommand',
                'No such command: \'notacommand\'',
                'cows> fwrite ' + fname,
            ])
        finally:
            os.remove(fname)

    def test_fwrite_other_view(self):
        _, fname = tempfile.mkstemp()
        cmd = 'fwrite %s cows' % fname
        try:
            with self.io:
                self.interface.do_command('view cows')
                self.interface.do_command('notacommand')
                self.interface.do_command('view msglog')
                self.interface.do_command(cmd)
            written = open(fname, 'r').read()
            self.assertEqual(written.split('\n'), [
                'cows> notacommand',
                'No such command: \'notacommand\'',
                'cows> view msglog',
            ])
        finally:
            os.remove(fname)

    def test_fwrite_wrong_num_args(self):
        with self.io:
            self.interface.do_command('fwrite')
            self.interface.do_command('fwrite blah blah blah')
        self.assertEqual(self.interface.view.contents, [
            'msglog> fwrite',
            'fwrite takes 1-2 args, got 0',
            'msglog> fwrite blah blah blah',
            'fwrite takes 1-2 args, got 3',
        ])
