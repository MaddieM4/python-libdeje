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

class DexterPrompt(object):
    def __init__(self, interface):
        self.interface = interface
        self.pstring   = '>>: '
        self.contents  = ''

    def draw(self):
        with self.terminal.location(0, self.terminal.height):
            print(self.pstring, self.contents)

    def wait(self):
        return input('hello')

    @property
    def terminal(self):
        return self.interface.terminal

    @property
    def display_string(self):
        return self.pstring + self.contents
