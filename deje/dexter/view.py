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

class DexterView(object):
    def __init__(self, interface, desc = None):
        self.interface = interface
        self.desc      = desc
        self.contents  = []

    def draw(self):
        self.terminal.view_win.erase()
        y_pos = self.terminal.height - 2
        x_max = self.terminal.width
        for line in reversed(self.contents):
            self.terminal.view_win.addstr(y_pos, 0, line[:x_max])
            y_pos -= 1
            if y_pos < 0:
                break
        self.terminal.view_win.refresh()

    def append(self, text):
        self.contents.extend(text.split('\n'))

    @property
    def terminal(self):
        return self.interface.terminal
