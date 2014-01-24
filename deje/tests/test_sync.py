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
from ejtp.router             import Router
from deje.owner              import Owner
from deje.handlers           import handler_document
from deje.tests.identity     import identity
from deje.protocol.message   import DEJEMessage

try:
   from Queue import Queue
except:
   from queue import Queue

class TestDocumentSync(unittest.TestCase):
    def setUp(self):
        self.router = Router()
        self.io     = IOMock()
        self.owners = {}
        self.msgs   = []
        self.save_serialization = False

    def setup_client(self, name):
        ident = identity(name)
        owner = Owner(ident, self.router)
        owner.identities.sync(
            *(other.identities for other in self.owners.values())
        )
        doc = handler_document('tag_team')
        owner.own_document(doc)
        owner.test_doc  = doc
        owner.test_name = name

        def on_ejtp(msg, client):
            self.msgs.append(DEJEMessage(msg, client, owner))
            owner.on_ejtp(msg, client)
        owner.client.rcv_callback = on_ejtp

        self.owners[name] = owner
        return owner

    def debug_contents(self, owner):
        '''
        Used for better diffing. Turn on with self.save_serialization.
        '''
        if not self.save_serialization:
            return
        import json
        json.dump(
            owner.test_doc.serialize(),
            open(owner.test_name, 'w'),
            indent=2
        )

    def assertSameDocState(self, msg_prefix=''):
        first = None
        for name in self.owners:
            owner = self.owners[name]
            self.debug_contents(owner)
            if first == None:
                first = owner
            else:
                msg = '%s: %s != %s' % (
                    msg_prefix,
                    first.test_name,
                    owner.test_name
                )
                self.assertEqual(
                    first.test_doc.serialize(),
                    owner.test_doc.serialize(),
                    msg
                )

    def format_msg(self, msg):
        extra = None
        if msg.type == 'deje-error':
            extra = msg.content

        if extra == None:
            return (msg.sender[2], msg.receiver[2], msg.type)
        else:
            return (msg.sender[2], msg.receiver[2], msg.type, extra)

    def test_min_existing(self):
        # Use mitzi as leader, atlas for consensus
        mitzi = self.setup_client("mitzi")
        atlas = self.setup_client("atlas")
        mitzi.test_doc.event({
            'path':     '/demo',
            'property': 'content',
            'value':    'A jolly good demo.',
        })

        # Make sure we are all on the same page before adding victor
        self.assertSameDocState("before sync")

        # Initialization should bring victor up to date
        victor = self.setup_client("victor")
        waiter = Queue()
        def on_finished():
            waiter.put("Finished")
        with self.io:
            victor.test_doc.sync(on_finished)
        waiter.get(timeout=0.5)
        self.assertSameDocState("after sync")
