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
try:
   from Queue import Queue
except:
   from queue import Queue

from ejtp.identity.core  import Identity
from deje.tests.ejtp     import TestEJTP

class TestSub(TestEJTP):
    def test_add(self):
        self.assertEqual(
            self.victor.protocol.subscribers(self.vdoc),
            tuple()
        )
        returned = Queue()
        def on_subscribe(sub):
            returned.put(sub)

        sources = [self.mitzi.identity, self.atlas.identity]
        self.victor.protocol.subscribe(
            self.vdoc,
            on_subscribe,
            sources
        )
        for _ in range(len(sources)):
            sub = returned.get(timeout=0.1)
            self.assertEqual(sub.target, self.victor.identity.location)
            self.assertEqual(sub.doc, self.vdoc.name)
            self.assertIn(sub.source, [x.location for x in sources])
        for doc in (self.mdoc, self.adoc):
            self.assertIn(self.victor.identity, doc.subscribers)

    def test_remove(self):
        adds = Queue()
        rms  = Queue()

        # Subscribed via mitzi but not atlas
        self.victor.protocol.subscribe(
            self.vdoc,
            lambda sub: adds.put(sub),
            [self.mitzi.identity]
        )

        sub = adds.get(timeout=0.1)
        self.assertEqual(
            self.mitzi.protocol.find('deje-sub').subscriptions,
            {
                sub.hash(): sub
            }
        )

        self.victor.protocol.unsubscribe(
            self.vdoc,
            lambda success: rms.put(success),
            sub
        )

        rm = rms.get(timeout=0.1)
        self.assertEqual(
            self.mitzi.protocol.find('deje-sub').subscriptions,
            {}
        )
        self.assertEqual(rm, True)
        for doc in (self.mdoc, self.adoc):
            self.assertNotIn(self.victor.identity, doc.subscribers)

        # Do it again, after already removed
        self.victor.protocol.unsubscribe(
            self.vdoc,
            lambda success: rms.put(success),
            sub
        )

        rm = rms.get(timeout=0.1)
        self.assertEqual(rm, False)

        # Try on atlas, who we were never subbed to
        sub.source = self.atlas.identity.location
        self.victor.protocol.unsubscribe(
            self.vdoc,
            lambda success: rms.put(success),
            sub
        )

        rm = rms.get(timeout=0.1)
        self.assertEqual(rm, False)

    def test_list(self):
        adds  = Queue()
        lists = Queue()

        # Subscribed via mitzi but not atlas
        self.victor.protocol.subscribe(
            self.vdoc,
            lambda sub: adds.put(sub),
            [self.mitzi.identity]
        )

        # Block on subscription
        add = adds.get(timeout=0.1)

        self.victor.protocol.get_subs(
            self.mitzi.identity,
            lambda subs: lists.put(('mitzi', subs))
        )
        self.victor.protocol.get_subs(
            self.atlas.identity,
            lambda subs: lists.put(('atlas', subs))
        )

        results = {}
        for _ in range(2):
            responder, subs = lists.get(timeout=0.1)
            results[responder] = subs

        self.assertEqual(
            results['mitzi'],
            { add.hash().export() : add }
        )
        self.assertEqual(
            results['atlas'],
            {}
        )
