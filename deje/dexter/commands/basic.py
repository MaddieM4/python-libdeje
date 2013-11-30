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

from deje.dexter.commands.group import DexterCommandGroup

class DexterCommandsBasic(DexterCommandGroup):
    def do_quit(self, args):
        '''
        Exit the program.

        Does not save anything, and doesn't ask either.
        '''
        quit(0)

    def do_help(self, args):
        '''
        A simple little help message.

        You can also view full descriptions with "help commandname".
        '''
        if len(args):
            lines = self._do_help_with_args(args)
        else:
            lines = self._do_help_no_args()
        for line in lines:
            self.output(line)

    def _do_help_with_args(self, args):
        lines = []
        for command in args:
            try:
                desc = self.get_description(command)
            except:
                desc = ['No such command.']
            desc[0] = command + " :: " + desc[0]
            lines.extend(desc)
        return lines

    def _do_help_no_args(self):
        return [
            'Dexter is a low-level DEJE client.',
            'It\'s perfect for low-level management of documents.',
            'Type "commands" to see the list of available commands.',
            'Type "help somecommand" to see more about a command.',
        ]

    def do_commands(self, args):
        '''
        List all available commands.
        '''
        commands = []
        for group in self.parent.groups:
            commands.extend(
                x[3:] for x in dir(group) if x.startswith('do_')
            )

        commands.sort()
        for command in commands:
            description = self.get_description(command)
            oneline     = description[0]
            self.output('%s :: %s' % (command, oneline))
