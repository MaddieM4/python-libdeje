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

import lupa

runtime = lupa.LuaRuntime()

class LuaInterpreter(object):
    def __init__(self, resource):
        self.resource = resource
        self.reload()

    def on_resource_update(self):
        self.call("on_resource_update")
        self.reload()

    def on_scratch_update(self):
        self.call("on_scratch_update")

    def call(self, event, *args):
        if event in self.lua_callbacks:
            return self.lua_callbacks[event](*args)

    def reload(self):
        self.lua_callbacks = runtime.execute(self.resource.content)

    @property
    def document(self):
        return self.resource.document
