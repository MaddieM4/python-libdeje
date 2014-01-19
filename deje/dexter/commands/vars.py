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
import copy

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

    def vset(self, chain, value):
        traverse_chain = chain[:-1]
        traverse_last  = chain[-1:]

        obj = self.traverse(traverse_chain)

        if len(traverse_last):
            last = normalize_key(obj, traverse_last[0])
            obj[last] = value
        else:
            # Setting the root data object
            self.interface.data = value

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

        chain = args[:-1]
        try:
            new_value = json.loads(args[-1])
        except:
            return self.output('Could not decode last parameter as JSON.')
        try:
            self.vset(chain, new_value)
        except TraversalError as e:
            return self.output(str(e))

    def do_vdel(self, args):
        '''
        Delete a value from variable storage.

        Dexter has a storage area for JSON-compatible data.
        The 'vdel' command deletes part of that data, based
        on the given path.

        For example, 

        msglog> vdel music artists

        is a bit like doing 

        >>> music = data["music"]
        >>> del temp["artists"]

        in Python. Arguments are only cast to ints when
        accessing array elements - map elements may only be
        accessed with string keys. The final argument is parsed
        as JSON.
        '''
        if len(args) < 1:
            self.interface.data = {}
            return
        traverse_chain = args[:-1]
        delete_key     = args[-1]

        try:
            obj = self.traverse(traverse_chain)
            delete_key = normalize_key(obj, delete_key)
            try:
                del obj[delete_key]
            except (KeyError, IndexError):
                raise TraversalError('Failed to find key', delete_key)
        except TraversalError as e:
            return self.output(str(e))

    def do_vclone(self, args):
        '''
        Copy variable data from one location to another.

        vclone always takes the following arguments:

        * -f or -b (forward or backward)
        * top-level variable name
        * deep-path variable (0 or more arguments)

        This is because it's difficult to express two deep
        paths in a single command, without bending over
        backwards to escape things. You are always cloning
        between a top-level location and a deep-path location.

        To copy between two deep-paths, you want to use a
        top-level location as an intermediate copy, and then
        vdel the top-level location afterwards to clean it
        up.

        Cloning forwards means copying from top-level to
        deep-path. Cloning backwards means copying from
        deep-path to top-level. The naming comes from the
        fact that the top-level location always comes first
        in the arguments.
        '''
        self.verify_num_args('vclone', len(args), 2, None)

        direction, tl_key = args[:2]
        dp_chain = args[2:]

        if not (direction in ('-f', '-b')):
            return self.output('Expected first argument to be -f or -b.')

        try:
            if direction == '-f':
                return self.clone([tl_key], dp_chain)
            else:
                return self.clone(dp_chain, [tl_key])
        except TraversalError as e:
            return self.output(str(e))

    def clone(self, source_chain, dest_chain):
        value = self.traverse(source_chain)
        self.vset(dest_chain, copy.deepcopy(value))

    def do_vsave(self, args):
        '''
        Save a variable value to disk.

        This command takes 1-2 arguments... a filename, and an
        optional variable name (if no variable name is given,
        the entire variable storage area is serialized to the
        file.

        Can only serialize top-level values or root.
        '''
        self.verify_num_args('vsave', len(args), 1, 2)

        filename = args[0]
        traverse_chain = args[1:]

        try:
            obj = self.traverse(traverse_chain)
        except TraversalError as e:
            return self.output(str(e))

        try:
            outstr = json.dumps(obj)
        except:
            return self.output("JSON serialization error")

        self.fwrite(filename, outstr)

    def do_vload(self, args):
        '''
        Load a variable value from disk.

        This command takes 1-2 arguments... a filename, and an
        optional variable name (if no variable name is given,
        the entire variable storage area is deserialized from
        the file.

        Can only deserialize to top-level values or root.
        '''
        self.verify_num_args('vload', len(args), 1, 2)

        filename = args[0]
        newobj = self.fread(filename)

        try:
            newobj = json.loads(newobj)
        except:
            return self.output("JSON serialization error")

        if len(args) == 1:
            self.interface.data = newobj
        else:
            key = args[1]
            self.interface.data[key] = newobj
