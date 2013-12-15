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
        y_pos = self.terminal.height - 2
        x_max = self.terminal.width
        lines = list(self.contents)
        while y_pos >= 0:
            if len(lines):
                line = lines.pop()
            else:
                line = ''
            outstr = line[:x_max].ljust(x_max)
            self.terminal.stdscr.addstr(y_pos, 0, outstr)
            y_pos -= 1

    def append(self, text):
        self.contents.extend(text.split('\n'))

    @property
    def terminal(self):
        return self.interface.terminal
