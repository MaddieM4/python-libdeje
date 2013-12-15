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

import curses

class Terminal(object):
    def __init__(self):
        self.setup()

    def setup(self):
        self.stdscr = curses.initscr()

    def stop(self):
        curses.endwin()

    def __enter__(self):
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)

        return self

    def __exit__(self, *args):
        self.stop()

    def getch(self):
        return self.stdscr.getch()

    def on_resize(self):
        self.stop()
        self.setup()

    @property
    def height(self):
        return self.stdscr.getmaxyx()[0]

    @property
    def width(self):
        return self.stdscr.getmaxyx()[1]
