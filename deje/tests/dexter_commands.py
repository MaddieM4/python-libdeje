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

from ejtp.util.compat        import unittest
from ejtp.tests.test_scripts import IOMock

from deje.dexter.interface   import DexterInterface
#from deje.tests.dummy_curses import DummyCursesTerminal

class DexterDemoGroup(object):
    def __init__(self):
        self.log_obj = []

    def do_demo(self, args):
        self.log_obj.append(args)

class DexterCommandTester(unittest.TestCase):
    def setUp(self):
        self.io = IOMock()
        with self.io:
            self.interface = DexterInterface()
            self.commands  = self.interface.commands
            self.terminal  = self.interface.terminal

        self.demo_group = DexterDemoGroup()
        self.commands.groups.add(self.demo_group)

    def tearDown(self):
        with self.terminal:
            pass

    def get_line(self, y):
        width  = self.terminal.width
        return ''.join(
            chr(self.terminal.stdscr.inch(y, x))
            for x in range(width)
        )
        
    def get_lines(self):
        height = self.terminal.height
        return [
            self.get_line(y) for y in range(height)
        ]

    def blank_lines(self, n):
        return [self.blank_line] * n

    @property
    def blank_line(self):
        return ' ' * self.terminal.width

    @property
    def demo_log(self):
        return self.demo_group.log_obj
