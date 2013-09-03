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

class Event(object):
    def __init__(self, content, author, version = None):
        self.content  = content
        self.author   = author
        self.version  = version

    @property
    def quorum_threshold_type(self):
        return "write"

    def ready(self, quorum, document):
        '''
        Returns whether the conditions are right to enact this Event.
        '''
        return quorum.done and self not in document._history.events

    def enact(self, quorum, document):
        document._history.add_event(self)
        self.apply(document._current)
        if document.owner:
            quorum.transmit_complete(document)

    @property
    def transmit_data(self):
        return {
            'type': 'deje-event',
            'version': self.version,
            'event': self.content,
            'author': self.authorname,
        }

    def apply(self, state):
        '''
        Apply event to a given HistoryState.
        '''
        state.apply(self)

    def test(self, state):
        return state.interpreter.event_test(self.content, self.author)

    @property
    def authorname(self):
        return self.author.name
        
    @property
    def hashcontent(self):
        return [self.content, self.version, self.authorname]

    def hash(self):
        return checksum(self.hashcontent)