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

class TraversalError(KeyError):
    def __str__(self):
        return "%s: %r" % self.args

def normalize_key(obj, key):
    '''
    If necessary, cast the key to the correct type for indexing obj,
    and return the correctly-typed key.
    '''
    if isinstance(obj, list) or isinstance(obj, tuple):
        # Doesn't catch everything fancy, but good enough.
        # Generally, real-world data will be loaded from JSON
        # files anyways, which is a reasonable sanitary thing.
        return int(key)
    elif isinstance(obj, dict):
        return str(key)
    else:
        raise TraversalError('Cannot inspect properties of object', obj)

class DexterCommandsVars(DexterCommandGroup):
    def traverse(self, keys):
        obj = self.interface.data
        for key in keys:
            key = normalize_key(obj, key)
            try:
                obj = obj[key]
            except (KeyError, IndexError):
                raise TraversalError('Failed to find key', key)
        return obj

    def do_vget(self, args):
        '''
        Print a value in variable storage.

        Dexter has a storage area for JSON-compatible data.
        The 'vget' command prints an object in storage, based
        on the given path.

        For example, 

        msglog> vget music artists "Professor Kliq"

        is a bit like doing 

        >>> print(data["music"]["artists"]["Professor Kliq")

        in Python. Arguments are only cast to ints when
        accessing array elements - map elements may only be
        accessed with string keys.
        '''
        try:
            obj = self.traverse(args)
        except TraversalError as e:
            return self.output(str(e))
        self.output(json.dumps(obj, indent = 2, sort_keys=True))

    def do_vset(self, args):
        '''
        Set a value in variable storage.

        Dexter has a storage area for JSON-compatible data.
        The 'vset' command stores an object there, based on
        the given path and contents.

        For example, 

        msglog> vset music {}

        is a bit like doing 

        >>> data["music"] = {}

        in Python. Arguments are only cast to ints when
        accessing array elements - map elements may only be
        accessed with string keys. The final argument is parsed
        as JSON.
        '''
        if len(args) < 1:
            self.output("Not enough arguments, expected at least 1.")
        traverse_chain = args[:-2]
        traverse_last  = args[-2:-1]
        try:
            new_value = json.loads(args[-1])
        except:
            return self.output('Could not decode last parameter as JSON.')
        try:
            obj = self.traverse(traverse_chain)
        except TraversalError as e:
            return self.output(str(e))

        if len(traverse_last):
            try:
                last = normalize_key(obj, traverse_last[0])
            except TraversalError as e:
                return self.output(str(e))
            obj[last] = new_value
        else:
            # Setting the root data object
            self.interface.data = new_value
