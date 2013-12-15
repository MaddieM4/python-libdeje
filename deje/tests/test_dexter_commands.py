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

class TestDexterCommands(DexterCommandTester):

    def test_get_args_one_word(self):
        result = self.commands.get_args('demo')
        self.assertEqual(result, ['demo'])

    def test_missing(self):
        with self.io:
            self.interface.do_command("notacommand")
        self.maxDiff = None
        self.assertEqual(self.interface.view.contents, [
            "msglog> notacommand",
            "No such command: 'notacommand'",
        ])

    def test_blank(self):
        with self.io:
            self.interface.do_command('')
        self.assertEqual(self.interface.view.contents, [
            "msglog> ",
        ])

    def test_command_only(self):
        with self.io:
            self.interface.do_command('demo')
        self.assertEqual(self.interface.view.contents, [
            "msglog> demo",
        ])
        self.assertEqual(
            self.demo_log.pop(),
            []
        )

    def test_command_with_args(self):
        with self.io:
            self.interface.do_command('demo this that "the other thing"')
        self.assertEqual(self.interface.view.contents, [
            'msglog> demo this that "the other thing"',
        ])
        self.assertEqual(
            self.demo_log.pop(),
            ['this', 'that', 'the other thing']
        )

    def test_command_with_bad_args(self):
        '''
        Induce a failure in shlex.split.
        '''
        with self.io:
            self.interface.do_command('demo "there is no end quote')
        self.assertEqual(self.interface.view.contents, [
            'msglog> demo "there is no end quote',
            'Command parse error: No closing quotation',
        ])
