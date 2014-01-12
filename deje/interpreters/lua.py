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

from ejtp.identity.core import Identity
from deje.interpreters import api
from deje.lua import Runtime, LuaObject, LuaCastError

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

    def call(self, event, **kwargs):
        if 'returntype' in kwargs:
            returntype = kwargs['returntype']
            del kwargs['returntype']
        else:
            returntype = object

        runtime = Runtime(deje = self.deje_module)
        runtime.set_globals(kwargs)

        if event in self.resource.content:
            funcbody = self.resource.content[event]
            result = runtime.execute(funcbody)
            self.api.process_queue()
        else:
            result = LuaObject(None)

        try:
            return result.cast(returntype)
        except LuaCastError as e:
            raise HandlerReturnError("Handler returned unexpected type", e)

    def normalize_idents(self, identlist):
        results = []
        for ident in identlist:
            if LuaObject(ident).is_list:
                ident = LuaObject(ident).to_list()
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
