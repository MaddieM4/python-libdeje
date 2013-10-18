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

from ejtp.util.hasher import checksum

class Action(object): # the only time I've wished the base class was called "lawsuit"
    def init(self, items={}):
        self.items = dict(items)

    def specific(self):
        '''
        Returns the appropriate subclass based on action type.
        '''
        if self.atype == "get_version":
            from djdns.read import ReadRequest
            return ReadRequest(self['author'])
        elif self.atype == "event":
            from djdns.event import Event
            return Event(self['items'], self['author'], self['version'])
        else:
            raise ValueError("Invalid action type %r" % self.atype)

    def hash(self):
        '''
        Less important role in new value-passing quorum scheme.
        '''
        return checksum(self.items)


    def __repr__(self):
        return "<Action %r by %r>" % (self.atype, self.author)

    def __contains__(self, k):
        return k in self.items

    def __getitem__(self, k):
        return self.items[k]

    def __setitem__(self, k, v):
        self.items[k] = v

    def __delitem__(self, k):
        del self.items[k]


    @property
    def atype(self):
        if 'type' in self:
            return self['type']

    @atype.setter
    def atype(self, v):
        self['type'] = v

    @property
    def author(self):
        if 'author' in self:
            return self['author']

    @author.setter
    def author(self, v):
        self['author'] = v
