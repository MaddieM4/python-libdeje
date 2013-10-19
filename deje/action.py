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
from ejtp.identity import Identity

class Action(object):
    def __init__(self, items={}, cache = None):
        self.deserialize(items, cache)

    def deserialize(self, items, cache = None):
        self.overflow = dict(items)
        self.atype  = self.overflow.pop('type')
        self.author = self.overflow.pop('author')

        if not isinstance(self.author, Identity):
            if cache:
                self.author = cache.find_by_location(self.author)
            else:
                raise TypeError("Author must be ejtp.identity.Identity")

    def serialize(self):
        items = self.items
        items['author'] = items['author'].location
        return items

    @property
    def items(self):
        result = {
            "type"   : self.atype,
            "author" : self.author,
        }
        result.update(self.overflow)
        return result

    @property
    def quorum_threshold_type(self):
        return None

    @property
    def authorname(self):
        return self.author.name

    def specific(self):
        '''
        Returns the appropriate subclass based on action type.
        '''
        if self.atype == "get_version":
            from deje.read import ReadRequest
            return ReadRequest(self.author)
        elif self.atype == "event":
            from deje.event import Event
            return Event(
                self.overflow['content'],
                self.author,
                self.overflow['version']
            )
        else:
            raise ValueError("Invalid action type %r" % self.atype)

    def hash(self):
        '''
        Less important role in new value-passing quorum scheme.
        '''
        return checksum(self.serialize())

    def valid(self, doc):
        if self.quorum_threshold_type == 'write':
            authorized = doc.can_write(self.author)
        elif self.quorum_threshold_type == 'read':
            authorized = doc.can_read(self.author)
        else:
            authorized = False
        return authorized and self.test(doc._current)


    def __repr__(self):
        return "<Action %r by %r>" % (self.atype, self.author)

    def __contains__(self, k):
        return k in self.items

    def __getitem__(self, k):
        return self.items[k]
