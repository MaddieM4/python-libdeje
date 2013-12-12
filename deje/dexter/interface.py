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

from deje.dexter.terminal import Terminal
from deje.dexter.view     import DexterView
from deje.dexter.commands import DexterCommands
from deje.dexter.prompt   import DexterPrompt

INITIAL_VIEWS = {
    'msglog': 'Shows all EJTP messages going in or out.',
}

class DexterInterface(object):
    def __init__(self, filename = None, terminal = None):
        self.filename = filename
        self.data     = {}
        self.commands = DexterCommands(self)
        self.prompt   = DexterPrompt(self)
        self.init_views()
        self.init_terminal(terminal)

    def init_terminal(self, terminal = None):
        self.terminal = terminal or Terminal()
        signal.signal(signal.SIGWINCH, self.on_resize)
        self.redraw()

    def init_views(self):
        self.views    = {}
        self.cur_view = 'msglog'
        for name, desc in INITIAL_VIEWS.items():
            self.views[name] = DexterView(self, desc)

    def on_resize(self, *args):
        self.terminal.on_resize()
        self.redraw()

    def redraw(self):
        self.view.draw()
        self.prompt.draw()
        self.terminal.stdscr.refresh()

    def do_command(self, command):
        self.output(self.prompt.pstring + command)
        self.commands.do(command)
        self.redraw()

    def output(self, text, name=None):
        name = name or self.cur_view
        self.get_view(name).append(text)

    def repl(self):
        with self.terminal:
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
