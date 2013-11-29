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

    def do_quit(self, args):
        quit(0)
