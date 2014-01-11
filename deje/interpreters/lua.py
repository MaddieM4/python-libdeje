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

def castFromLua(value, expected_type):
    if expected_type == list and tableIsList(value):
        return tableToList(value)
    elif expected_type == dict and tableIsDict(value):
        return tableToDict(value)
    elif isinstance(value, expected_type):
        return value
    # If value was valid, we would have returned already
    raise HandlerReturnError(
        'Could not cast %r to %r' % (value, expected_type)
    )

def set_runtime_globals(runtime, variables):
    lua_g = runtime.eval('_G')
    for key in variables:
        lua_g[key] = variables[key]

class LuaInterpreter(object):
    def __init__(self, resource):
        '''
            Lua-based interpreter for handler files.
        '''
        self.resource = resource
        self.api = api.API(self)

    # Callbacks

    def on_resource_update(self, path, propname, oldpath=None):
        self.call(
            "on_resource_update",
            path=path,
            propname=propname,
            oldpath=oldpath
        )

    def on_event_achieve(self, ev, author, state=None):
        set_resource, sr_flag = self.api.set_resource(state)
        self.call(
            "on_event_achieve",
            set_resource=set_resource,
            ev=ev,
            author=author
        )
        sr_flag.revoke()

    def event_test(self, ev, author):
        return self.call(
            "event_test",
            ev=ev,
            author=author,
            returntype = bool
        )

    def quorum_participants(self):
        return self.normalize_idents(
            self.call("quorum_participants", returntype = list)
        )

    def quorum_thresholds(self):
        return self.call("quorum_thresholds", returntype = dict)

    def can_read(self, ident):
        return self.call(
            "can_read",
            name=ident.name,
            returntype = bool
        )

    def can_write(self, ident):
        return self.call(
            "can_write",
            name=ident.name,
            returntype = bool
        )

    def request_protocols(self):
        return self.call("request_protocols", returntype = list)

    def host_request(self, callback, params):
        self.call(
            "on_host_request",
            callback=callback,
            params=params
        )

    # Misc

    def setup_runtime(self, **global_vars):
        runtime = lupa.LuaRuntime()
        set_runtime_globals(runtime, global_vars)
        return runtime

    def call(self, event, **kwargs):
        if 'returntype' in kwargs:
            returntype = kwargs['returntype']
            del kwargs['returntype']
        else:
            returntype = object

        runtime = self.setup_runtime(deje = self.deje_module)
        set_runtime_globals(runtime, kwargs)

        if event in self.resource.content:
            funcbody = self.resource.content[event]
            result = runtime.execute(funcbody)
            self.api.process_queue()
        else:
            result = None

        return castFromLua(result, returntype)

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
