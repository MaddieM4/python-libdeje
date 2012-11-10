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
import api

bootstrap = '''
deje = {}
function load_deje(module)
    deje = module
end
return load_deje
'''

class LuaInterpreter(object):
    def __init__(self, resource):
        '''
            Lua-based interpreter for handler files.
        '''
        self.resource = resource
        self.runtime = lupa.LuaRuntime()
        self.api = api.API(self.document)

        # Provide the deje module
        bootstrapfunc = self.runtime.execute(bootstrap)
        bootstrapfunc(self.api.export())
        self.runtime.execute('load_deje = nil')

        self.reload()
        self.call("on_load")

    def on_resource_update(self, path, propname, oldpath=None):
        self.call("on_resource_update", path, propname, oldpath)
        self.reload()

    def on_scratch_update(self, author):
        self.call("on_scratch_update", author)

    def call(self, event, *args):
        callback = self.runtime.eval(event)
        if callback and callable(callback):
            result = callback(*args)
            self.api.process_queue()
            return result
        else:
            raise TypeError("Cannot call object %r", callback)

    def reload(self):
        self.runtime.execute(self.resource.content)

    def debug(self, response):
        print response

    @property
    def document(self):
        return self.resource.document
