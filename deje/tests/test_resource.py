from ejtp.util.compat import unittest

from deje.resource import Resource

class TestMimetypes(unittest.TestCase):

    def test_valid_resource(self):
        r = Resource(type='text/html')

    def test_invalid_resource(self):
        self.assertRaises(ValueError, Resource, type='invalid/type')

    def test_direct_json(self):
        r = Resource(type='direct/json')

