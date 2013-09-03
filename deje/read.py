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
from deje import quorum

class ReadRequest(object):
    def __init__(self, subscriber):
        self.subscriber = subscriber
        self.done = False

    @property
    def quorum_threshold_type(self):
        return "read"

    def is_done(self, document):
        '''
        Returns whether Request has already been granted.
        '''
        return self.done

    def enact(self, quorum, document):
        '''
        Add subscriber to list.
        '''
        self.done = True
        # Did we promise to be one of the subscribed-to parties?
        if quorum.sig_valid(document.identity.key):
            document.subscribers.add(self.subscriber.key)

    @property
    def transmit_data(self):
        return {
            'type': 'deje-subscribe',
            'subscriber': self.subscriber.location,
        }

    @property
    def version(self):
        return None

    @property
    def hashcontent(self):
        return self.subscriber.key

    def hash(self):
        return checksum(self.hashcontent)

    @property
    def author(self):
        return self.subscriber
