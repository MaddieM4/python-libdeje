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
    def __init__(self, interface):
        self.interface = interface
        self.contents  = []

    def draw(self):
        total_lines = self.terminal.height - 1
        y_pos = 0
        for line in self.contents[-total_lines:]:
            with self.terminal.location(0, y_pos):
                print(line[:self.terminal.width])
            y_pos += 1

    def append(self, text):
        self.contents.append(text.split('\n'))

    @property
    def terminal(self):
        return self.interface.terminal
