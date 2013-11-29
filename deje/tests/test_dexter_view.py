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

from deje.dexter.view        import DexterView
from deje.dexter.interface   import DexterInterface
from deje.tests.blessings    import DummyBlessingsTerminal

class TestDexterView(unittest.TestCase):
    def setUp(self):
        self.io = IOMock()
        with self.io:
            self.terminal  = DummyBlessingsTerminal()
            self.interface = DexterInterface(terminal = self.terminal)
            self.view      = DexterView(self.interface)

    def test_append_no_newline(self):
        self.view.append("Hello world")
        self.assertEqual(self.view.contents, ["Hello world"])

    def test_append_with_newlines(self):
        self.view.append("ABC\nDEF\nGHI")
        self.assertEqual(self.view.contents, ["ABC","DEF","GHI"])

    def test_multiple_append(self):
        self.view.append("Line 1")
        self.view.append("Line 2\nLine 3")
        self.assertEqual(self.view.contents, ["Line 1","Line 2","Line 3"])

    def test_draw_empty(self):
        with self.io:
            self.view.draw()
        self.assertEqual(self.io.get_lines(), [
            'CONTEXT ENTER: location(0,0)',
            'clear',
            'CONTEXT EXIT:  location(0,0)',
            'CONTEXT ENTER: location(0,60)',
            '>>:',
            'CONTEXT EXIT:  location(0,60)',
        ])

    def test_draw_one_line(self):
        with self.io:
            self.view.append("Hello")
            self.view.draw()
        self.assertEqual(self.io.get_lines(), [
            'CONTEXT ENTER: location(0,0)',
            'clear',
            'CONTEXT EXIT:  location(0,0)',
            'CONTEXT ENTER: location(0,60)',
            '>>:',
            'CONTEXT EXIT:  location(0,60)',
            'CONTEXT ENTER: location(0,59)',
            'Hello',
            'CONTEXT EXIT:  location(0,59)',
        ])

    def test_draw_two_lines(self):
        with self.io:
            self.view.append("Hello\nworld")
            self.view.draw()
        self.assertEqual(self.io.get_lines(), [
            'CONTEXT ENTER: location(0,0)',
            'clear',
            'CONTEXT EXIT:  location(0,0)',
            'CONTEXT ENTER: location(0,60)',
            '>>:',
            'CONTEXT EXIT:  location(0,60)',
            'CONTEXT ENTER: location(0,58)',
            'Hello',
            'CONTEXT EXIT:  location(0,58)',
            'CONTEXT ENTER: location(0,59)',
            'world',
            'CONTEXT EXIT:  location(0,59)',
        ])

    def test_draw_long_line(self):
        with self.io:
            self.view.append("q" * 85)
            self.view.draw()
        self.assertEqual(self.io.get_lines(), [
            'CONTEXT ENTER: location(0,0)',
            'clear',
            'CONTEXT EXIT:  location(0,0)',
            'CONTEXT ENTER: location(0,60)',
            '>>:',
            'CONTEXT EXIT:  location(0,60)',
            'CONTEXT ENTER: location(0,59)',
            'q' * 80, # Trimmed to terminal width
            'CONTEXT EXIT:  location(0,59)',
        ])

