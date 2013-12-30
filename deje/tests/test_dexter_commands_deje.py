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

from ejtp.client   import Client
from deje.owner    import Owner
from deje.document import Document

from deje.handlers.lua          import handler_document
from deje.tests.dexter_commands import DexterCommandTester, Tempfile

import time
import json

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

    def test_dinit_no_docname(self):
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
            'Need to set variable \'docname\'',
        ])

    def test_dinit_no_docserialized(self):
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
            'docname' : 'example',
        }
        with self.io:
            self.interface.do_command('dinit')
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'Need to set variable \'docserialized\'',
        ])

    def test_dinit_no_such_identity(self):
        self.interface.data = {
            'identity': ["local", None, "jackson"],
            'idcache' : {},
            'docname' : None,
            'docserialized' : None,
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
            'docname' : None,
            'docserialized' : None,
        }
        with self.io:
            self.interface.do_command('dinit')
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'Could not deserialize data in idcache',
        ])

    def test_dinit_bad_docname(self):
        location = ["local", None, "jackson"]
        self.interface.data = {
            'identity': ["local", None, "jackson"],
            'idcache' : {
                '["local",null,"jackson"]': {
                    'location': location,
                    'name': 'daniel@sgc.gov',
                    'encryptor': ['rotate', 4],
                }
            },
            'docname' : None,
            'docserialized' : None,
        }
        with self.io:
            self.interface.do_command('dinit')
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'Not a valid docname: null',
        ])

    def test_dinit_bad_docserialized(self):
        location = ["local", None, "jackson"]
        self.interface.data = {
            'identity': ["local", None, "jackson"],
            'idcache' : {
                '["local",null,"jackson"]': {
                    'location': location,
                    'name': 'daniel@sgc.gov',
                    'encryptor': ['rotate', 4],
                }
            },
            'docname' : 'example',
            'docserialized' : None,
        }
        with self.io:
            self.interface.do_command('dinit')
        expected = [
            'msglog> dinit',
            'Failed to deserialize data:',
        ]
        # Get Python-version-specific error repr
        try:
            None[5]
        except TypeError as e:
            expected.append(repr(e))
        self.assertEqual(self.interface.view.contents, expected)


    def test_dinit_success(self):
        location  = ["local", None, "jackson"]
        docserial = handler_document('echo_chamber').serialize()
        self.interface.data = {
            'identity': location,
            'idcache' : {
                '["local",null,"jackson"]': {
                    'location': location,
                    'name': 'daniel@sgc.gov',
                    'encryptor': ['rotate', 4],
                }
            },
            'docname': 'example',
            'docserialized': docserial
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
        self.assertIsInstance(self.interface.document, Document)
        self.assertEqual(self.interface.document.name, 'example')
        self.assertEqual(
            self.interface.document.serialize(),
            docserial
        )


    def test_other_no_init(self):
        with self.io:
            self.interface.do_command('devent')
            self.interface.do_command('dget_latest')
            self.interface.do_command('dvexport')
            self.interface.do_command('dexport')
        self.assertEqual(self.interface.view.contents, [
            'msglog> devent',
            'DEJE not initialized, see dinit command',
            'msglog> dget_latest',
            'DEJE not initialized, see dinit command',
            'msglog> dvexport',
            'DEJE not initialized, see dinit command',
            'msglog> dexport',
            'DEJE not initialized, see dinit command',
        ])

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
            'docname': 'example',
            'docserialized': handler_document('echo_chamber').serialize()
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

    def test_msg_solo_transmit(self):
        with self.io:
            self.interface.owner.transmit(
                self.interface.document,
                "example",
                {},
                participants = True,
                subscribers  = False,
            )
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'DEJE initialized',
            '["local",null,"jackson"] (ME) : example',
            '["local",null,"jackson"] : example',
            '["local",null,"jackson"] (ME) : deje-error',
            '["local",null,"jackson"] : deje-error',
        ])

    def test_dget_latest(self):
        with self.io:
            self.interface.do_command('dget_latest')
        self.assertEqual(self.interface.get_view('msglog').contents, [
            'msglog> dinit',
            'DEJE initialized',
            'msglog> dget_latest',
            '["local",null,"jackson"] (ME) : deje-paxos-accept',
            '["local",null,"jackson"] : deje-paxos-accept',
            '["local",null,"jackson"] (ME) : deje-paxos-accepted',
            '["local",null,"jackson"] : deje-paxos-accepted',
            '["local",null,"jackson"] (ME) : deje-paxos-complete',
            '["local",null,"jackson"] : deje-paxos-complete',
            '["local",null,"jackson"] (ME) : deje-action-completion',
            '["local",null,"jackson"] : deje-action-completion',
        ])
        self.assertEqual(self.interface.get_view('doc').contents, [
            'Document latest version is \'current\'',
        ])

    def test_dvexport_wrong_num_args(self):
        with self.io:
            self.interface.do_command('dvexport')
            self.interface.do_command('dvexport a b')
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'DEJE initialized',
            'msglog> dvexport',
            'dvexport takes exactly 1 arg(s), got 0',
            'msglog> dvexport a b',
            'dvexport takes exactly 1 arg(s), got 2',
        ])

    def test_dvexport(self):
        with self.io:
            self.interface.do_command('dvexport x')
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'DEJE initialized',
            'msglog> dvexport x',
        ])
        self.assertEqual(
            self.interface.data['x'],
            self.interface.document.serialize()
        )

    def test_dexport_wrong_num_args(self):
        with self.io:
            self.interface.do_command('dexport')
            self.interface.do_command('dexport a b')
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'DEJE initialized',
            'msglog> dexport',
            'dexport takes exactly 1 arg(s), got 0',
            'msglog> dexport a b',
            'dexport takes exactly 1 arg(s), got 2',
        ])

    def test_dexport(self):
        with Tempfile() as fname:
            cmd = 'dexport ' + fname
            with self.io:
                self.interface.do_command(cmd)
            written = open(fname, 'r').read()
        self.assertEqual(
            json.loads(written),
            self.interface.document.serialize()
        )
        self.assertEqual(self.interface.view.contents, [
            'msglog> dinit',
            'DEJE initialized',
            'msglog> ' + cmd,
        ])
