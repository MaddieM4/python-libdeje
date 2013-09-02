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
from ejtp.identity.cache import IdentityCache
from ejtp.router         import Router
from deje.tests.ejtp     import TestEJTP

from deje.owner          import Owner
from deje.tests.identity import identity
from deje.handlers.lua   import handler_document, handler_text
from deje.resource       import Resource

try:
   from Queue import Queue
except:
   from queue import Queue

class TestOwnerSimple(unittest.TestCase):

    def test_init_string_ident(self):
        # Make sure string idents fail
        self.assertRaises(
            AttributeError,
            Owner,
            "anonymous", Router()
        )

    def test_init_no_location(self):
        # Make sure self_idents with no location fail
        badident = identity()
        badident.location = None
        self.assertRaises(
            TypeError,
            Owner,
            badident, None, False
        )

    def test_init(self):
        # Do setup for testing a good owner.
        owner = Owner(identity(), make_jack = False)

        key = String('["local",null,"mitzi"]')
        self.assertIsInstance(owner.identities, IdentityCache)
        self.assertIn(key, owner.identities)
        self.assertIsInstance(owner.identities[key], Identity)

        doc = handler_document("echo_chamber")
        self.assertIsInstance(doc.handler, Resource)
        owner.own_document(doc)

class TestOwnerEJTP(TestEJTP):
    def test_on_ejtp(self):
        self.assertEqual(
            self.mitzi.identity.location,
            ['local', None, 'mitzi']
        )
        self.assertEqual(
            self.atlas.identity.location,
            ['local', None, 'atlas']
        )
        self.assertEqual(
            self.mitzi.client.interface,
            self.mitzi.identity.location
        )

        r = self.mitzi.client.router
        self.assertEqual(
            r.client(self.mitzi.identity.location),
            self.mitzi.client
        )
        self.assertEqual(
            self.atlas.client.interface,
            self.atlas.identity.location
        )
        self.assertEqual(
            self.mitzi.client.router,
            self.atlas.client.router
        )

        # Test raw EJTP connectivity with a malformed message
        self.atlas.client.write_json(
            self.mitzi.identity.location,
            "Oompa loompa"
        )
        self.assertEqual(
            self.getOutput().replace("u'", "'"),
            "Error from 'mitzi@lackadaisy.com', code 30: " +
            "'Recieved non-{} message, dropping'\n"
        )

    def test_get_version(self):
        queue = Queue()
        def on_recv_version(version):
            queue.put("Version is %r" % str(version))

        targets = self.victor.get_version(self.vdoc, on_recv_version)
        self.assertEqual(queue.get(timeout=0.1), "Version is 'current'")

        mev = self.mdoc.event({
            'path':'/example',
            'property':'content',
            'value':'Mitzi says hi',
        })
        self.victor.get_version(self.vdoc, on_recv_version)
        self.assertEqual(queue.get(timeout=0.1), "Version is '5d5cde1b1b090ced74fabdb44d4e97a430dc0b5d'")

    def test_get_block(self):
        queue = Queue()
        def on_recv_block(block):
            queue.put(block)

        # Put in a event to retrieve

        mev = self.mdoc.event({
            'path':'/example',
            'property':'content',
            'value':'Mitzi says hi',
        })

        # Retrieve event

        self.victor.get_block(self.vdoc, self.mdoc.version, on_recv_block)
        result = queue.get(timeout=0.1)
        self.assertEqual(
            sorted(result.keys()),
            ['author', 'content', 'signatures', 'version']
        )
        self.assertEqual(result['author'], 'mitzi@lackadaisy.com')
        self.assertEqual(
            result['content'],
            {
                "path": "/example", 
                "property": "content", 
                "value": "Mitzi says hi"
            }
        )
        self.assertEqual(
            sorted(result['signatures'].keys()),
            ['["local",null,"atlas"]', '["local",null,"mitzi"]']
        )
        self.assertEqual(result['version'], self.mdoc.version.export())

    def test_get_snapshot(self):
        queue = Queue()
        expected = {
            "/handler.lua": {
                "comment": "tag_team", 
                "content": handler_text('tag_team'),
                "path": "/handler.lua", 
                "type": "text/lua"
            }
        }
        def on_recv_snapshot(snapshot):
            queue.put(snapshot)

        self.victor.get_snapshot(self.vdoc, self.vdoc.version, on_recv_snapshot)
        result = queue.get(timeout=0.1)
        self.assertEqual(result, expected)
