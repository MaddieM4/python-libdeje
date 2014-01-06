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

from ejtp.util.compat    import unittest
from deje.handlers       import handler_resource
from deje.tests.identity import identity

from deje.history        import History
from deje.historystate   import HistoryState
from deje.resource       import Resource
from deje.event          import Event

class TestHistory(unittest.TestCase):

    def setUp(self):
        self.mitzi = identity('mitzi')
        self.atlas = identity('atlas')

        self.res_default = Resource()
        self.res_tt      = handler_resource("tag_team")
        self.ev_default  = Event({'hello':'world'}, self.mitzi)
        self.ev_tt       = Event(
            {
                'path' : '/handler.lua',
                'property' : 'comment',
                'value' : 'An arbitrary comment',
            },
            self.atlas
        )
        self.hs1         = HistoryState(None, [self.res_default])
        self.hs2         = HistoryState("example", [self.res_default, self.res_tt])

    def test_init(self):
        hist = History()
        self.assertEqual(hist.states, {})
        self.assertEqual(hist.events, [])
        self.assertEqual(hist.events_by_hash, {})

    def test_init_states(self):
        hist = History([self.hs1, self.hs2])

        self.assertEqual(hist.states, {
            None : self.hs1,
            "example" : self.hs2,
        })
        self.assertEqual(hist.events, [])
        self.assertEqual(hist.events_by_hash, {})

    def test_init_events(self):
        hist = History(events=[self.ev_default, self.ev_tt])
        self.assertEqual(hist.states, {})
        self.assertEqual(hist.events, [self.ev_default, self.ev_tt])
        self.assertEqual(hist.events_by_hash, {
            self.ev_default.hash(): self.ev_default,
            self.ev_tt.hash():      self.ev_tt,
        })

    def test_init_both(self):
        hist = History([self.hs1, self.hs2], [self.ev_default, self.ev_tt])
        self.assertEqual(hist.states, {
            None : self.hs1,
            "example" : self.hs2,
        })
        self.assertEqual(hist.events, [self.ev_default, self.ev_tt])
        self.assertEqual(hist.events_by_hash, {
            self.ev_default.hash(): self.ev_default,
            self.ev_tt.hash():      self.ev_tt,
        })

    def test_orphan_states(self):
        hist = History()
        self.assertEqual(hist.orphan_states, [])

        hist.add_event(self.ev_default)
        self.assertEqual(hist.orphan_states, [])

        self.hs1.hash = self.ev_default.hash()
        hist.add_states([self.hs1, self.hs2])
        self.assertEqual(hist.orphan_states, [self.hs2])

    def test_orphan_events(self):
        hist = History()
        self.assertEqual(hist.orphan_events, [])

        hist.add_event(self.ev_default)
        self.assertEqual(hist.orphan_events, [self.ev_default])

        self.hs1.hash = self.ev_default.hash()
        hist.add_states([self.hs1, self.hs2])
        self.assertEqual(hist.orphan_events, [])

        hist.add_event(self.ev_tt)
        self.assertEqual(hist.orphan_events, [self.ev_tt])
