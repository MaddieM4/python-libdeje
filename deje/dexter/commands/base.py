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

import shlex

from deje.dexter.commands.basic import DexterCommandsBasic
from deje.dexter.commands.views import DexterCommandsViews
from deje.dexter.commands.files import DexterCommandsFiles
from deje.dexter.commands.vars  import DexterCommandsVars

class DexterCommands(object):
    def __init__(self, interface):
        self.interface = interface
        self.groups    = set([
            DexterCommandsBasic(self),
            DexterCommandsViews(self),
            DexterCommandsFiles(self),
            DexterCommandsVars(self),
        ])

    def do(self, cmdstr):
        args = self.get_args(cmdstr)
        if not len(args):
            return
        try:
            func = self.get_handler(args[0])
        except KeyError:
            self.output('No such command: %r' % args[0])
            return

        func(args[1:])

    def get_args(self, cmdstr):
        return shlex.split(cmdstr)

    def get_handler(self, command):
        funcname  = 'do_' + command
        for group in self.groups:
            if hasattr(group, funcname):
                return getattr(group, funcname)
        raise KeyError("No such command", command)

    def get_description(self, command):
        func = self.get_handler(command)
        raw  = func.__doc__
        if not (func and raw):
            return ['No description available.']
        return [s.strip() for s in raw.strip().split('\n')]

    @property
    def output(self):
        return self.interface.output
