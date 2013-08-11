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

from ejtp.util.compat import unittest

from deje.resource import Resource

class TestMimetypes(unittest.TestCase):

    def test_valid_resource(self):
        r = Resource(type='text/html')

    def test_invalid_resource(self):
        self.assertRaises(ValueError, Resource, type='invalid/type')

    def test_direct_json(self):
        r = Resource(type='direct/json')

