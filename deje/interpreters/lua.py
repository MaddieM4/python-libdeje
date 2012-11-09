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

        # Provide the deje module
        bootstrapfunc = self.runtime.execute(bootstrap)
        bootstrapfunc({
            'get_resource': lambda path: self.document.get_resource(path),
            'get_scratch':  lambda auth: self.document._scratchspace[auth],
            'debug': self.debug,
        })
        self.runtime.execute('load_deje = nil')

        self.reload()
        self.call("on_load")

    def on_resource_update(self):
        self.call("on_resource_update")
        self.reload()

    def on_scratch_update(self):
        self.call("on_scratch_update")

    def call(self, event, *args):
        callback = self.runtime.eval(event)
        if callback:
            return callback(*args)

    def reload(self):
        self.runtime.execute(self.resource.content)

    def debug(self, response):
        print response

    @property
    def document(self):
        return self.resource.document
