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

import shlex

class DexterCommands(object):
    def __init__(self, interface):
        self.interface = interface

    def do(self, cmdstr):
        args = self.get_args(cmdstr)
        if not len(args):
            return
        func = self.get_handler(args[0])
        if func != None:
            func(args[1:])
        else:
            self.interface.output('No such command: %r' % args[0])

    def get_args(self, cmdstr):
        return shlex.split(cmdstr)

    def get_handler(self, command):
        funcname  = 'do_' + command
        if hasattr(self, funcname):
            return getattr(self, funcname)
        else:
            return None

    def get_description(self, command):
        raw = getattr(self, 'do_' + command).__doc__
        if not raw:
            return ['No description available.']
        return [s.strip() for s in raw.strip().split('\n')]

    def do_quit(self, args):
        '''
        Exit the program.

        Does not save anything, and doesn't ask either.
        '''
        quit(0)

    def do_help(self, args):
        '''
        A simple little help message.
        '''
        self.output('Dexter is a low-level DEJE client.')
        self.output('It\'s perfect for low-level management of documents.')
        self.output('Type "commands" to see the list of available commands.')

    def do_commands(self, args):
        '''
        List all available commands.
        '''
        commands = [x[3:] for x in dir(self) if x.startswith('do_')]
        commands.sort()
        for command in commands:
            description = self.get_description(command)
            oneline     = description[0]
            self.output('%s :: %s' % (command, oneline))

    @property
    def output(self):
        return self.interface.output
