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
    def __init__(self, hash = None, resources = []):
        self.hash = hash
        self.resources = {}
        for r in resources:
            self.add_resource(r)

    def add_resource(self, resource):
        self.resources[resource.path] = resource

    def enact(self, event):
        event.enact(self)

    def clone(self):
        return HistoryState(
            self.hash,
            [r.clone() for r in self.resources.values()]
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
        }
