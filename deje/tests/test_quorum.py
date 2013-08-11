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

from deje.checkpoint import Checkpoint
from deje.handlers.lua import handler_document
from deje.tests.identity import identity
from deje.owner import Owner

class TestQuorum(unittest.TestCase):

    def setUp(self):
        self.doc = handler_document("echo_chamber")
        self.cp  = Checkpoint(self.doc, {'x':'y'}, 0, 'mick-and-bandit')
        self.quorum = self.cp.quorum
        self.ident = identity()
        self.owner = Owner(self.ident, make_jack=False)
        self.owner.own_document(self.doc)

    def test_clear(self):
        self.quorum.sign(self.ident)
        self.assertEqual(self.quorum.completion, 1)

        self.quorum.clear()
        self.assertEqual(self.quorum.completion, 0)

    def test_completion(self):
        self.assertEqual(self.quorum.completion, 0)
        self.quorum.sign(self.ident)
        self.assertEqual(self.quorum.completion, 1)

    def test_outdated(self):
        self.assertEqual(self.doc.version, 0)
        self.assertEqual(self.quorum.version, 0)
        self.assertFalse(self.quorum.outdated)

        self.quorum.sign(self.ident)
        self.assertFalse(self.quorum.outdated)

        self.cp.enact()
        # Checkpoint '{'x': 'y'}' achieved.

        self.assertEqual(self.doc.version, 1)
        self.assertEqual(self.quorum.version, 0)
        self.assertTrue(self.quorum.outdated)

    def test_participants(self):
        self.assertEqual(self.quorum.participants, ['mitzi@lackadaisy.com'])

    def test_thresholds(self):
        self.assertEqual(self.quorum.thresholds, {'read':1, 'write':1})

    def test_threshold(self):
        self.assertEqual(self.quorum.threshold, 1)
