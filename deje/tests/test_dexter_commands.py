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

from __future__ import absolute_import, print_function

from ejtp.util.compat        import unittest
from ejtp.tests.test_scripts import IOMock

from deje.dexter.interface   import DexterInterface
from deje.tests.blessings    import DummyBlessingsTerminal

class TestDexterCommands(unittest.TestCase):
    def setUp(self):
        self.io = IOMock()
        with self.io:
            self.terminal  = DummyBlessingsTerminal()
            self.interface = DexterInterface(terminal = self.terminal)
            self.commands  = self.interface.commands

        self.cb_log = []
        self.commands.do_demo = lambda args: self.cb_log.append(args)

    def test_get_args_one_word(self):
        result = self.commands.get_args('demo')
        self.assertEqual(result, ['demo'])

    def test_missing(self):
        with self.io:
            self.interface.do_command("notacommand")
        self.assertEqual(self.io.get_lines(), [
            "CONTEXT ENTER: location(0,0)",
            "clear",
            "CONTEXT EXIT:  location(0,0)",
            "CONTEXT ENTER: location(0,60)",
            "msglog>",
            "CONTEXT EXIT:  location(0,60)",
            "CONTEXT ENTER: location(0,0)",
            "clear",
            "CONTEXT EXIT:  location(0,0)",
            "CONTEXT ENTER: location(0,58)",
            "msglog> notacommand",
            "CONTEXT EXIT:  location(0,58)",
            "CONTEXT ENTER: location(0,59)",
            "No such command: 'notacommand'",
            "CONTEXT EXIT:  location(0,59)",
            "CONTEXT ENTER: location(0,60)",
            "msglog>",
            "CONTEXT EXIT:  location(0,60)",
        ])

    def test_blank(self):
        with self.io:
            self.interface.do_command('')
        self.assertEqual(self.io.get_lines(), [
            "CONTEXT ENTER: location(0,0)",
            "clear",
            "CONTEXT EXIT:  location(0,0)",
            "CONTEXT ENTER: location(0,60)",
            "msglog>",
            "CONTEXT EXIT:  location(0,60)",
            "CONTEXT ENTER: location(0,0)",
            "clear",
            "CONTEXT EXIT:  location(0,0)",
            "CONTEXT ENTER: location(0,59)",
            "msglog>",
            "CONTEXT EXIT:  location(0,59)",
            "CONTEXT ENTER: location(0,60)",
            "msglog>",
            "CONTEXT EXIT:  location(0,60)",
        ])

    def test_command_only(self):
        with self.io:
            self.interface.do_command('demo')
        self.assertEqual(self.io.get_lines(), [
            "CONTEXT ENTER: location(0,0)",
            "clear",
            "CONTEXT EXIT:  location(0,0)",
            "CONTEXT ENTER: location(0,60)",
            "msglog>",
            "CONTEXT EXIT:  location(0,60)",
            "CONTEXT ENTER: location(0,0)",
            "clear",
            "CONTEXT EXIT:  location(0,0)",
            "CONTEXT ENTER: location(0,59)",
            "msglog> demo",
            "CONTEXT EXIT:  location(0,59)",
            "CONTEXT ENTER: location(0,60)",
            "msglog>",
            "CONTEXT EXIT:  location(0,60)",
        ])
        self.assertEqual(
            self.cb_log.pop(),
            []
        )

    def test_command_with_args(self):
        with self.io:
            self.interface.do_command('demo this that "the other thing"')
        self.assertEqual(self.io.get_lines(), [
            "CONTEXT ENTER: location(0,0)",
            "clear",
            "CONTEXT EXIT:  location(0,0)",
            "CONTEXT ENTER: location(0,60)",
            "msglog>",
            "CONTEXT EXIT:  location(0,60)",
            "CONTEXT ENTER: location(0,0)",
            "clear",
            "CONTEXT EXIT:  location(0,0)",
            "CONTEXT ENTER: location(0,59)",
            'msglog> demo this that "the other thing"',
            "CONTEXT EXIT:  location(0,59)",
            "CONTEXT ENTER: location(0,60)",
            "msglog>",
            "CONTEXT EXIT:  location(0,60)",
        ])
        self.assertEqual(
            self.cb_log.pop(),
            ['this', 'that', 'the other thing']
        )

    def test_help(self):
        with self.io:
            self.interface.do_command('help')
        self.assertEqual(self.interface.view.contents, [
            'msglog> help',
            'Dexter is a low-level DEJE client.',
            'It\'s perfect for low-level management of documents.',
            'Type "commands" to see the list of available commands.',
        ])

    def test_commands(self):
        with self.io:
            self.interface.do_command('commands')
        self.assertEqual(self.interface.view.contents, [
            'msglog> commands',
            'commands :: List all available commands.',
            'demo :: No description available.',
            'help :: A simple little help message.',
            'quit :: Exit the program.',
        ])
