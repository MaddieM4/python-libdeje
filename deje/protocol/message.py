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

from __future__ import absolute_import

from deje.action import Action

class DEJEMessage(object):
    '''
    Provides common functionality for recieved messages.
    '''

    def __init__(self, msg, client, owner):
        self.msg     = msg
        self.client  = client
        self.owner   = owner
        self.content = msg.unpack()

    def __getitem__(self, k):
        return self.content[k]

    def __contains__(self, k):
        return k in self.content

    @property
    def sender(self):
        return self.msg.sender

    @property
    def receiver(self):
        return self.msg.receiver

    @property
    def type(self):
        return self['type']

    @property
    def qid(self):
        return self['qid']

    @property
    def doc(self):
        if 'docname' in self:
            return self.owner.documents[self['docname']]
        else:
            return None

    @property
    def action(self):
        return Action(self['action'], self.owner.identities).specific()
