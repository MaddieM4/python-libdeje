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

from deje.resource import Resource

class HistoryState(object):
    '''
    A set of resources that can be cloned, or have events applied to it.

    A document will generally want at least two HistoryStates - a starting
    point, and a current state. The current state can always be derived from
    the initial state and a series of events.

    The truly initial state will have a hash value of None. After that, the
    hash is the same as the hash of the associated Event. All Events have a
    hash.
    '''
    def __init__(self, hash = None, resources = [], handler_path="/handler.lua", doc = None):
        self.doc  = doc
        self.hash = hash
        self.handler_path = handler_path
        self.resources = {}
        for r in resources:
            self.add_resource(r)

        self._interpreter = (None, None) # hash, interp

    def add_resource(self, resource):
        resource.document = self.doc
        self.resources[resource.path] = resource

    def get_resource(self, path):
        return self.resources[path]

    def apply(self, event):
        '''
        Apply an event to this state.

        Does not check event validity, or incur side effects aside from
        invalidating the current interpreter.
        '''
        self.interpreter.on_event_achieve(event.content, event.author, self)
        self.hash = event.hash()

    def clone(self):
        '''
        Create a full distinct copy of this HistoryState in memory.
        '''
        return HistoryState(
            self.hash,
            [r.clone() for r in self.resources.values()],
            self.handler_path,
            self.doc
        )

    def serialize_resources(self):
        serialized = {}
        for resource in self.resources.values():
            serialized[resource.path] = resource.serialize()
        return serialized

    def serialize(self):
        return {
            "hash" : self.hash,
            "resources" : self.serialize_resources(),
            "handler" : self.handler_path,
        }

    def deserialize(self, serial):
        self.hash         = serial['hash']
        self.handler_path = serial['handler']

        for r_serial in serial['resources'].values():
            r_real = Resource()
            r_real.deserialize(r_serial)
            self.add_resource(r_real)

    @property
    def handler(self):
        return self.resources[self.handler_path]

    def create_interpreter(self):
        return self.handler.interpreter()

    @property
    def interpreter(self):
        i = self._interpreter
        if i[0] == self.hash and i[1]:
            return i[1]
        else:
            new_interp = self.create_interpreter()
            self._interpreter = (self.hash, new_interp)
            return new_interp
