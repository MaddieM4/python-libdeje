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

from __future__ import print_function
import lupa
from deje.interpreters import api

if not "callable" in globals():
    import collections
    def callable(obj):
        return isinstance(obj, collections.Callable)

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

    # Callbacks

    def on_resource_update(self, path, propname, oldpath=None):
        self.call("on_resource_update", path, propname, oldpath)
        self.reload()

    def on_checkpoint_achieve(self, cp, author):
        set_resource, sr_flag = self.api.set_resource()
        self.call("on_checkpoint_achieve", set_resource, cp, author)
        sr_flag.revoke()

    def checkpoint_test(self, cp, author):
        return self.call("checkpoint_test", cp, author, returntype = bool)

    def quorum_participants(self):
        if not self.cache['quorum_participants']:
            self.cache['quorum_participants'] = \
                self.call("quorum_participants", returntype = list)
        return self.cache['quorum_participants']

    def quorum_thresholds(self):
        if not self.cache['quorum_thresholds']:
            self.cache['quorum_thresholds'] = \
                self.call("quorum_thresholds", returntype = dict)
        return self.cache['quorum_thresholds']

    def can_read(self, ident):
        if hasattr(ident, 'name'):
            ident = ident.name
        return self.call("can_read", ident, returntype = bool)

    def can_write(self, ident):
        if hasattr(ident, 'name'):
            ident = ident.name
        return self.call("can_write", ident, returntype = bool)

    def request_protocols(self):
        if not self.cache['request_protocols']:
            self.cache['request_protocols'] = \
                self.call("request_protocols", returntype = list)
        return self.cache['request_protocols']

    def host_request(self, callback, params):
        self.call("on_host_request", callback, params)

    # Misc

    def call(self, event, *args, **kwargs):
        returntype = ("returntype" in kwargs and kwargs["returntype"]) or object
        callback = self.runtime.eval(event)
        if callback and callable(callback):
            result = callback(*args)
            self.api.process_queue()
            self.reset_cache()
            if returntype == dict and isinstance(result, lupa._lupa._LuaTable):
                return dict(result)
            if returntype == list and isinstance(result, lupa._lupa._LuaTable):
                return list(result.values())
            elif isinstance(result, returntype):
                return result
            # If value was valid, we would have returned already
            raise HandlerReturnError(
                '%s(%s) returned %r, %r expected' % (
                    event,
                    ",".join(repr(x) for x in args),
                    result,
                    returntype
                )
            )
        else:
            raise TypeError("Cannot call object %r", callback)

    def eval(self, value):
        return self.runtime.eval(value)

    def execute(self, value):
        return self.runtime.execute(value)

    def reload(self):
        self.reset_cache()
        self.runtime.execute(self.resource.content)

    def reset_cache(self):
        self.cache = {
            'quorum_participants': False,
            'quorum_thresholds': False,
            'request_protocols': False,
        }

    def debug(self, response):
        print(response)

    @property
    def document(self):
        return self.resource.document

class HandlerReturnError(Exception): pass
