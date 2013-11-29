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

from __future__ import print_function

import sys

def stderr(*args):
    print(*args, file=sys.stderr)

class DummyContext(object):
    def __init__(self, label):
        self.label  = label

    def __enter__(self):
        stderr("CONTEXT ENTER: " + self.label)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        stderr("CONTEXT EXIT:  " + self.label)

class DummyBlessingsTerminal(object):
    '''
    Class used for mocking/tests. Assumes that IO is being caught by an
    IOMock object, such that we can just print to stderr.
    '''

    def __init__(self, width=80, height=60):
        self.width  = width
        self.height = height

    def clear(self):
        return "clear"

    def location(self, x = None, y = None):
        return DummyContext("location(%r,%r)" % (x,y))
