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

class Tempfile(str):
    def __enter__(self):
        _, self.path = tempfile.mkstemp()
        return self.path

    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.remove(self.path)

class TestDexterBasicGroup(DexterCommandTester):

    def test_fwrite_current_view(self):
        with Tempfile() as fname:
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

    def test_fwrite_other_view(self):
        with Tempfile() as fname:
            cmd = 'fwrite %s cows' % fname
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

    def test_fread_current_view(self):
        with Tempfile() as fname:
            open(fname, 'w').write('\n'.join([
                'demo abc',
                'demo def',
            ]))
            cmd = 'fread ' + fname
            with self.io:
                self.interface.do_command(cmd)
            self.assertEqual(self.interface.view.contents, [
                'msglog> ' + cmd,
                'msglog> demo abc',
                'msglog> demo def',
            ])
            self.assertEqual(self.demo_log, [
                ['abc'],
                ['def'],
            ])

    def test_fread_other_view(self):
        with Tempfile() as fname:
            open(fname, 'w').write('\n'.join([
                'demo abc',
                'demo def',
            ]))
            cmd = 'fread %s cows' % fname
            with self.io:
                self.interface.do_command(cmd)
            self.assertEqual(self.interface.get_view('msglog').contents, [
                'msglog> ' + cmd,
            ])
            self.assertEqual(self.interface.get_view('cows').contents, [
                'cows> demo abc',
                'cows> demo def',
            ])
            self.assertEqual(self.demo_log, [
                ['abc'],
                ['def'],
            ])

    def test_fread_wrong_num_args(self):
        with self.io:
            self.interface.do_command('fread')
            self.interface.do_command('fread blah blah blah')
        self.assertEqual(self.interface.view.contents, [
            'msglog> fread',
            'fread takes 1-2 args, got 0',
            'msglog> fread blah blah blah',
            'fread takes 1-2 args, got 3',
        ])
