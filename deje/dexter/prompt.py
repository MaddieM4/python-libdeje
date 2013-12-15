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

from __future__ import print_function, absolute_import
import sys
import curses

DIRECTION_KEYS = (
    curses.KEY_LEFT,
    curses.KEY_RIGHT,
    curses.KEY_UP,
    curses.KEY_DOWN,
    curses.KEY_SF,
    curses.KEY_SR,
    curses.KEY_NPAGE,
    curses.KEY_PPAGE,
    curses.KEY_MOVE,
)

IGNORE_KEYS = (
    curses.KEY_RESIZE,
)

class DexterPrompt(object):
    def __init__(self, interface):
        self.interface = interface
        self.current   = ""
        self.history   = []

    def draw(self):
        width  = self.terminal.width
        height = self.terminal.height
        outstr = self.pstring + self.current

        y = height - 1
        x = min(len(outstr), width-1)

        self.terminal.stdscr.insstr(y,0, outstr.ljust(width))
        self.terminal.stdscr.move(y, x)
        self.terminal.stdscr.cursyncup()

    def _wait(self):
        while 1:
            c = self.terminal.getch()
            if c == ord('\n'):
                self.history.append(self.current)
                self.current = ""
                return self.history[-1]
            elif c == curses.KEY_BACKSPACE:
                self.current = self.current[:-1]
            elif c in DIRECTION_KEYS:
                pass
            elif c in IGNORE_KEYS:
                pass
            else:
                try:
                    self.current += chr(c)
                except ValueError:
                    pass
            self.interface.redraw()

    def wait(self):
        try:
            return self._wait()
        except KeyboardInterrupt:
            return "quit"

    @property
    def terminal(self):
        return self.interface.terminal

    @property
    def pstring(self):
        return self.interface.cur_view + '> '
