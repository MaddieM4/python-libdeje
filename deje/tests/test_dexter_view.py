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

from ejtp.util.compat import unittest
from deje.dexter.view import DexterView

class DummyInterface(object):
    pass

class TestDexterView(unittest.TestCase):
    def setUp(self):
        self.interface = DummyInterface()
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
