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

import json

from deje.dexter.commands.group import DexterCommandGroup

class DexterCommandsVars(DexterCommandGroup):
    def do_get(self, args):
        '''
        Print a value in variable storage.

        Dexter has a storage area for JSON-compatible data.
        The 'get' command prints an object in storage, based
        on the given path.

        For example, 

        msglog> get music artists "Professor Kliq"

        is a bit like doing 

        >>> print(data["music"]["artists"]["Professor Kliq")

        in Python. Arguments are only cast to ints when
        accessing array elements - map elements may only be
        accessed with string keys.
        '''
        obj = self.interface.data
        for key in args:
            if isinstance(obj, list) or isinstance(obj, tuple):
                # Doesn't catch everything fancy, but good enough.
                # Generally, real-world data will be loaded from JSON
                # files anyways, which is a reasonable sanitary thing.
                key = int(key)
            try:
                obj = obj[key]
            except (KeyError, IndexError):
                self.output('Failed to find key %r' % key)
                return
        self.output(json.dumps(obj, indent = 2, sort_keys=True))
