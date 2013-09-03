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
        self.enacted  = False

    @property
    def quorum_threshold_type(self):
        return "read"

    def ready(self, quorum, document):
        '''
        Returns whether the conditions are right to enact this ReadRequest.
        '''
        return quorum.done and not self.enacted

    def enact(self, quorum, document):
        self.enacted = True
        if quorum.sig_valid(document.identity.key):
            document.subscribers.add(self.subscriber.key)
            if document.owner:
                quorum.transmit_complete(document)

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
