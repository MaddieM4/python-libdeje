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
from ejtp.identity.core import Identity
from deje.interpreters import api

if not "callable" in globals():
    import collections
    def callable(obj):
        return isinstance(obj, collections.Callable)

TABLE_CLASS = lupa._lupa._LuaTable

def tableToList(table):
    return [table[i+1] for i in range(max(table.keys()))]

def tableToDict(table):
    return dict(table)

def tableIsList(table):
    if not isinstance(table, TABLE_CLASS):
        return False
    for key in table.keys():
        if not isinstance(key, int):
            return False
    return True

def tableIsDict(table):
    # Returns true even for list, as any valid list is a valid dict
    return isinstance(table, TABLE_CLASS)

class LuaInterpreter(object):
    def __init__(self, resource):
        '''
            Lua-based interpreter for handler files.
        '''
        self.resource = resource
        self.api = api.API(self)

    # Callbacks

    def on_resource_update(self, path, propname, oldpath=None):
        self.call("on_resource_update", path, propname, oldpath)

    def on_event_achieve(self, ev, author, state=None):
        set_resource, sr_flag = self.api.set_resource(state)
        self.call("on_event_achieve", set_resource, ev, author)
        sr_flag.revoke()

    def event_test(self, ev, author):
        return self.call("event_test", ev, author, returntype = bool)

    def quorum_participants(self):
        return self.normalize_idents(
            self.call("quorum_participants", returntype = list)
        )

    def quorum_thresholds(self):
        return self.call("quorum_thresholds", returntype = dict)

    def can_read(self, ident):
        return self.call("can_read", ident.name, returntype = bool)

    def can_write(self, ident):
        return self.call("can_write", ident.name, returntype = bool)

    def request_protocols(self):
        return self.call("request_protocols", returntype = list)

    def host_request(self, callback, params):
        self.call("on_host_request", callback, params)

    # Misc

    def setup_runtime(self, **global_vars):
        runtime = lupa.LuaRuntime()
        lua_g = runtime.eval('_G')
        for key in global_vars:
            lua_g[key] = global_vars[key]
        return runtime

    def call(self, event, *args, **kwargs):
        runtime = self.setup_runtime(deje = self.deje_module)
        returntype = ("returntype" in kwargs and kwargs["returntype"]) or object
        funcbody = self.resource.content[event]
        runtime.execute(funcbody)
        function = runtime.eval(event)

        if not (function and callable(function)):
            raise TypeError("Cannot call object %r", function)

        result = function(*args)
        self.api.process_queue()
        if returntype == list and tableIsList(result):
            return tableToList(result)
        elif returntype == dict and tableIsDict(result):
            return tableToDict(result)
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

    def normalize_idents(self, identlist):
        results = []
        for ident in identlist:
            if tableIsList(ident):
                ident = tableToList(ident)
            if isinstance(ident, Identity):
                results.append(ident)
            else:
                results.append(self.owner.identities.find_by_name(ident))
        return results

    @property
    def deje_module(self):
        return self.api.export()

    @property
    def document(self):
        return self.resource.document

    @property
    def owner(self):
        return self.document.owner

class HandlerReturnError(Exception): pass
