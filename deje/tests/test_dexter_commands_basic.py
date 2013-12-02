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

class TestDexterBasicGroup(DexterCommandTester):

    def test_help(self):
        with self.io:
            self.interface.do_command('help')
        self.assertEqual(self.interface.view.contents, [
            'msglog> help',
            'Dexter is a low-level DEJE client.',
            'It\'s perfect for low-level management of documents.',
            'Type "commands" to see the list of available commands.',
            'Type "help somecommand" to see more about a command.',
        ])

    def test_help_with_args(self):
        with self.io:
            self.interface.do_command('help help commands blooby')
        self.assertEqual(self.interface.view.contents, [
            'msglog> help help commands blooby',
            'help :: A simple little help message.',
            '',
            'You can also view full descriptions with "help commandname".',
            'commands :: List all available commands.',
            'blooby :: No such command.',
        ])

    def test_commands(self):
        with self.io:
            self.interface.do_command('commands')
        self.assertEqual(self.interface.view.contents, [
            'msglog> commands',
            'commands :: List all available commands.',
            'demo :: No description available.',
            'fread :: Read contents of a file as a series of commands.',
            'fwrite :: Write contents of a view to a file.',
            'get :: Print a value in variable storage.',
            'help :: A simple little help message.',
            'quit :: Exit the program.',
            'set :: Set a value in variable storage.',
            'view :: List views, or select one.',
        ])
