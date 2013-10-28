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

import datetime

from ejtp.util.hasher import checksum

class Subscription(object):
    def __init__(self, source='', target='', doc='', expiration=None):
        self.source = source
        self.target = target
        self.doc    = doc
        self.expiration = expiration

    def serialize(self):
        return {
            'source': self.source,
            'target': self.target,
            'doc'   : self.doc,
            'expiration': self.expiration,
        }

    def deserialize(self, serialized):
        self.source = serialized['source']
        self.target = serialized['target']
        self.doc    = serialized['doc']
        self.expiration = serialized['expiration']

    def __eq__(self, other):
        if not isinstance(other, Subscription):
            return False
        return self.serialize() == other.serialize()

    def hash(self):
        return checksum(self.serialize())
