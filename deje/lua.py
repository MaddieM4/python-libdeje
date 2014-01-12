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

# TODO: Replace this file with the usage of HardLupa

import lupa

TABLE_CLASS   = lupa._lupa._LuaTable
RUNTIME_CLASS = lupa.LuaRuntime

class LuaCastError(ValueError): pass

class LuaObject(object):
    def __init__(self, value):
        if isinstance(value, LuaObject):
            self.value = value.value
        else:
            self.value = value

    def cast(self, expected_type):
        value = self.value
        if expected_type == list and self.is_list:
            return self.to_list()
        elif expected_type == dict and self.is_dict:
            return self.to_dict()
        elif isinstance(value, expected_type):
            return value
        # If value was valid, we would have returned already
        raise LuaCastError(
            'Could not cast %r to %r' % (value, expected_type)
        )

    def is_a(self, comparing_type):
        '''
        Determine if internal value is of the given type.
        '''
        if comparing_type == list:
            return self.is_list
        elif comparing_type == dict:
            return self.is_dict
        else:
            return isinstance(self.value, comparing_type)

    def to_list(self):
        table = self.value
        return [table[i+1] for i in range(max(table.keys()))]

    def to_dict(self):
        return dict(self.value)

    @property
    def is_list(self):
        if not isinstance(self.value, TABLE_CLASS):
            return False
        for key in self.value.keys():
            if not isinstance(key, int):
                return False
        return True

    @property
    def is_dict(self):
        # Returns true even for list, as any valid list is a valid dict
        return isinstance(self.value, TABLE_CLASS)

class Runtime(object):
    def __init__(self, **variables):
        self._runtime = RUNTIME_CLASS()
        self.set_globals(variables)

    @property
    def runtime(self):
        return self._runtime

    def set_globals(self, variables):
        lua_g = self.runtime.eval('_G')
        for key in variables:
            lua_g[key] = variables[key]

    def eval(self, code):
        return LuaObject(self.runtime.eval(code))

    def execute(self, code):
        return LuaObject(self.runtime.execute(code))
