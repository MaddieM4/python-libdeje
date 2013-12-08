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

from deje.owner import Owner

from deje.tests.dexter_commands import DexterCommandTester

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
