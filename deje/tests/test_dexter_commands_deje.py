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

from ejtp.client import Client
from deje.owner  import Owner

from deje.tests.dexter_commands import DexterCommandTester

import time

class TestDexterDEJEGroup(DexterCommandTester):

    def test_dinit_no_idcache(self):
        with self.io:
            self.interface.do_command('dinit')
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'Need to set variable \'idcache\'',
        ])

    def test_dinit_no_identity(self):
        self.interface.data = {
            'idcache' : {},
        }
        with self.io:
            self.interface.do_command('dinit')
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'Need to set variable \'identity\'',
        ])

    def test_dinit_no_such_identity(self):
        self.interface.data = {
            'identity': ["local", None, "jackson"],
            'idcache' : {},
        }
        with self.io:
            self.interface.do_command('dinit')
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'No identity in cache for ["local",null,"jackson"]',
        ])

    def test_dinit_idcache_read_failure(self):
        self.interface.data = {
            'identity': ["local", None, "jackson"],
            'idcache' : {'x':'yz'},
        }
        with self.io:
            self.interface.do_command('dinit')
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'Could not deserialize data in idcache',
        ])

    def test_dinit_success(self):
        location = ["local", None, "jackson"]
        self.interface.data = {
            'identity': location,
            'idcache' : {
                '["local",null,"jackson"]': {
                    'location': location,
                    'name': 'daniel@sgc.gov',
                    'encryptor': ['rotate', 4],
                }
            },
        }
        with self.io:
            self.interface.do_command('dinit')
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'DEJE initialized',
        ])
        self.assertIsInstance(self.interface.owner, Owner)
        self.assertEqual(
            self.interface.owner.identity,
            self.interface.owner.identities.find_by_location(location)
        )

class TestDexterDEJEGroupInitialized(DexterCommandTester):

    def setUp(self):
        # Reuse setup, without being subclass and pulling in tests
        DexterCommandTester.setUp(self)

        self.j_loc = ["local", None, "jackson"]
        self.t_loc = ["local", None, "tealc"]
        self.interface.data = {
            'identity': self.j_loc,
            'idcache' : {
                '["local",null,"jackson"]': {
                    'location': self.j_loc,
                    'name': 'daniel@sgc.gov',
                    'encryptor': ['rotate', 4],
                },
                '["local",null,"tealc"]': {
                    'location': self.t_loc,
                    'name': 'tealc@sgc.gov',
                    'encryptor': ['rotate', 5],
                },
            },
        }
        with self.io:
            self.interface.do_command('dinit')
        self.router = self.interface.owner.router
        self.tealc  = Client(
            self.router,
            self.t_loc,
            self.interface.owner.identities
        )
        self.daniel = self.interface.owner.client

    def test_basic_assertions(self):
        self.assertEqual(
            self.tealc.encryptor_cache,
            self.daniel.encryptor_cache
        )

    def test_msg_external_str(self):
        with self.io:
            self.tealc.write_json(
                self.j_loc,
                'Hello, world'
            )
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'DEJE initialized',
            '["local",null,"tealc"] : <could not parse>',
            '["local",null,"jackson"] (ME) : deje-error',
        ])

    def test_msg_external_map(self):
        with self.io:
            self.tealc.write_json(
                self.j_loc,
                {'type': 'example'}
            )
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'DEJE initialized',
            '["local",null,"tealc"] : example',
            '["local",null,"jackson"] (ME) : deje-error',
        ])

    def test_msg_external_valid(self):
        rcvd = []
        self.tealc.rcv_callback = lambda msg, client: rcvd.append(msg)
        with self.io:
            self.tealc.write_json(
                self.j_loc,
                {'type': 'deje-sub-list-query', 'qid':5}
            )
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'DEJE initialized',
            '["local",null,"tealc"] : deje-sub-list-query',
            '["local",null,"jackson"] (ME) : deje-sub-list-response',
        ])
        self.assertEqual(
            rcvd.pop().unpack(),
            {
                'type': 'deje-sub-list-response',
                'qid' : 5,
                'subs': {},
            }
        )

    def test_msg_sent_str(self):
        with self.io:
            self.interface.owner.client.write_json(
                self.t_loc,
                "Not even a mapping"
            )
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'DEJE initialized',
            '["local",null,"jackson"] (ME) : <msg type not provided>',
        ])

    def test_msg_sent_map(self):
        with self.io:
            self.interface.owner.client.write_json(
                self.t_loc,
                {"Does not have": "a type key"}
            )
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'DEJE initialized',
            '["local",null,"jackson"] (ME) : <msg type not provided>',
        ])

    def test_msg_sent_valid(self):
        with self.io:
            self.interface.owner.client.write_json(
                self.t_loc,
                {"type": "example"}
            )
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'DEJE initialized',
            '["local",null,"jackson"] (ME) : example',
        ])
