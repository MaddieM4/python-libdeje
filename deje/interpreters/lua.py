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

BOOTSTRAP = '''
deje = {}
function load_deje(module)
    deje = module
end
return load_deje
'''

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
        self.runtime = lupa.LuaRuntime()
        self.api = api.API(self.document)

        # Provide the deje module
        bootstrapfunc = self.runtime.execute(BOOTSTRAP)
        bootstrapfunc(self.api.export())
        self.runtime.execute('load_deje = nil')

        self.reload()

    # Callbacks

    def on_resource_update(self, path, propname, oldpath=None):
        self.call("on_resource_update", path, propname, oldpath)
        self.reload()

    def on_event_achieve(self, ev, author):
        set_resource, sr_flag = self.api.set_resource()
        self.call("on_event_achieve", set_resource, ev, author)
        sr_flag.revoke()

    def event_test(self, ev, author):
        return self.call("event_test", ev, author, returntype = bool)

    def quorum_participants(self):
        temp = []
        if not self.cache['quorum_participants']:
            temp = self.call("quorum_participants", returntype = list)
        self.cache['quorum_participants'] = self.normalize_idents(temp)
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
        else:
            raise TypeError("Cannot call object %r", callback)

    def normalize_idents(self, identlist):
        results = []
        for ident in identlist:
            if tableIsList(ident):
                ident = tableToList(ident)
            results.append(self.owner.identities.find_by_location(ident))
        return results

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

    @property
    def owner(self):
        return self.document.owner

class HandlerReturnError(Exception): pass
