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

import sys
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from ejtp.util.compat import unittest

class StreamTest(unittest.TestCase):
    def setUp(self):
        self._stdout = sys.stdout
        self.sio     = StringIO()
        sys.stdout   = self.sio

    def getOutput(self):
        output = self.sio.getvalue()
        self.sio.seek(0)
        self.sio.truncate()
        return output

    def assertOutput(self, text):
        self.assertEquals(text, self.getOutput())

    def tearDown(self):
        sys.stdout = self._stdout
