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

from persei import String

from ejtp.util.compat    import unittest
from ejtp.identity.core  import Identity
from deje.tests.ejtp     import TestEJTP

from deje.document import Document, save_to, load_from
from deje.resource import Resource
from deje.read     import ReadRequest

class TestDocumentSimple(unittest.TestCase):

    def setUp(self):
        self.doc = Document("testing")

    def test_serialize(self):
        expected_original = {
            'handler' : '/handler.lua',
            'hash' : None,
            'resources': {},
        }

        serial = self.doc.serialize()
        self.assertEqual(
            sorted(serial.keys()),
            ['events', 'original']
        )
        self.assertEqual(serial['original'], expected_original)
        self.assertEqual(serial['events'],   [])

        self.doc.add_resource(
            Resource(path="/example", content="example"),
            False
        )
        self.assertEqual(self.doc.serialize()['original'], expected_original)
        self.doc.freeze()
        self.assertEqual(
            self.doc.serialize()['original'],
            {
                'handler': '/handler.lua',
                'hash': 'current',
                'resources': {
                    '/example': {
                        'comment': '',
                        'content': 'example',
                        'path':    '/example',
                        'type':    'application/x-octet-stream'
                   }
                }
            }
        )

    def test_deserialize(self):
        self.doc.add_resource(
            Resource(path="/example", content="example"),
            False
        )
        self.doc.freeze()
        serial = self.doc.serialize()

        newdoc = Document(self.doc.name)
        newdoc.deserialize(serial)

        self.assertEqual(list(newdoc.resources.keys()), ['/example'])
        self.assertIsInstance(newdoc.resources['/example'], Resource)

        initial_resources = newdoc._initial.resources
        self.assertEqual(list(initial_resources.keys()), ['/example'])
        self.assertIsInstance(initial_resources['/example'], Resource)

    def test_saving(self):
        self.doc.add_resource(
            Resource(path="/example", content="example"),
            False
        )
        self.doc.freeze()

        save_to(self.doc, "example.dje")
        newdoc = load_from("example.dje")
        self.assertEqual(newdoc.serialize(), self.doc.serialize())

class TestDocumentEJTP(TestEJTP):

    def test_event(self):
        mev = self.mdoc.event({
            'path':'/example',
            'property':'content',
            'value':'Mitzi says hi',
        })
        self.assertEqual(self.mdoc.get_quorum(mev).completion, 2)
        self.assertEqual(self.mdoc.competing, [])

        self.assertEqual(
            self.mdoc.get_resource('/example').content,
            "Mitzi says hi"
        )
        self.assertEqual(
            self.adoc.get_resource('/example').content,
            "Mitzi says hi"
        )

    def test_subscribe(self):
        # Test a read
        self.assertEqual(self.vdoc.version, 'current')
        self.assertTrue(self.vdoc.can_read())

        # One error is normal, due to transmission patterns
        rr = self.vdoc.subscribe()
        self.assertEqual(
            self.getOutput().replace("u'", "'").replace('atlas','mitzi'),
            "Error from 'mitzi@lackadaisy.com', code 40: " +
            "'Unknown lock quorum data, dropping (fc7278eb74a4e0f24b00b06d9dc2147ddffa1673)'\n"
        )
        self.assertEqual(self.mdoc.competing, [])
        self.assertEqual(self.adoc.competing, [])

        self.assertIsInstance(rr, ReadRequest)

        for doc in (self.mdoc, self.adoc):
            subscribers = doc.subscribers
            self.assertIsInstance(subscribers, set)
            self.assertEqual(list(subscribers), [String('["local",null,"victor"]')])
