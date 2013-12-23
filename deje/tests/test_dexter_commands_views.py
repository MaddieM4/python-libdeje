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

from deje.tests.dexter_commands import DexterCommandTester

class TestDexterBasicGroup(DexterCommandTester):

    def test_view_list(self):
        with self.io:
            self.interface.do_command('view')
        self.assertEqual(self.interface.view.contents, [
            'msglog> view',
            'doc :: Document-level events and messages.',
            'msglog :: Shows all EJTP messages going in or out.',
        ])

    def test_view_switch(self):
        with self.io:
            self.interface.do_command('view cows')
            self.interface.do_command('view')
        self.assertEqual(
            sorted(list(self.interface.views.keys())),
            ['cows', 'doc', 'msglog']
        )
        self.assertEqual(self.interface.views['msglog'].contents, [
            'msglog> view cows',
        ])
        self.assertEqual(self.interface.views['cows'].contents, [
            'cows> view',
            'cows',
            'doc :: Document-level events and messages.',
            'msglog :: Shows all EJTP messages going in or out.',
        ])
