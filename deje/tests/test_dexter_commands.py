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

import os
import tempfile

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

    def test_view_list(self):
        with self.io:
            self.interface.do_command('view')
        self.assertEqual(self.interface.view.contents, [
            'msglog> view',
            'msglog :: Shows all EJTP messages going in or out.',
        ])

    def test_view_switch(self):
        with self.io:
            self.interface.do_command('view cows')
            self.interface.do_command('view')
        self.assertEqual(
            sorted(list(self.interface.views.keys())),
            ['cows', 'msglog']
        )
        self.assertEqual(self.interface.views['msglog'].contents, [
            'msglog> view cows',
        ])
        self.assertEqual(self.interface.views['cows'].contents, [
            'cows> view',
            'cows',
            'msglog :: Shows all EJTP messages going in or out.',
        ])

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

    def test_commands(self):
        with self.io:
            self.interface.do_command('commands')
        self.assertEqual(self.interface.view.contents, [
            'msglog> commands',
            'commands :: List all available commands.',
            'demo :: No description available.',
            'fwrite :: Write contents of a view to a file.',
            'help :: A simple little help message.',
            'quit :: Exit the program.',
            'view :: List views, or select one.',
        ])
