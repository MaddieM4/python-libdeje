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

import signal
import blessings

from deje.dexter.view     import DexterView
from deje.dexter.commands import DexterCommands
from deje.dexter.prompt   import DexterPrompt

class DexterInterface(object):
    def __init__(self, filename = None, terminal = None):
        self.filename = filename
        self.commands = DexterCommands(self)
        self.prompt   = DexterPrompt(self)
        self.terminal = terminal or blessings.Terminal()
        self.views    = {}
        self.cur_view = 'msglog'

        def on_resize(signum, frame):
            self.redraw()
        signal.signal(signal.SIGWINCH, on_resize)
        self.redraw()

    def redraw(self):
        with self.terminal.location(0,0):
            print(self.terminal.clear())
        self.view.draw()
        self.prompt.draw()

    def do_command(self, command):
        self.output(self.prompt.pstring + command)
        self.commands.do(command)
        self.redraw()

    def output(self, text, name=None):
        name = name or self.cur_view
        self.get_view(name).append(text)

    def repl(self):
        while True:
            cmd = self.prompt.wait()
            self.do_command(cmd)

    def get_view(self, name):
        if not name in self.views:
            self.views[name] = DexterView(self)
        return self.views[name]

    @property
    def view(self):
        return self.get_view(self.cur_view)
