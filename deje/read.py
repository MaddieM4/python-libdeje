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

from deje import quorum

class ReadRequest(object):
    def __init__(self, document, subscriber=None):
        self.document = document
        self.subscriber = subscriber or document.identity
        self.enacted  = False
        self.quorum   = quorum.Quorum(
                            self,
                            "read",
                        )
        self.document._qs.register(self.quorum)

    def sign(self, *args, **kwargs):
        self.quorum.sign(*args, **kwargs)
        if self.owner:
            if self.subscriber == self.owner.identity:
                self.transmit()
            else:
                self.quorum.transmit(self.document)

    def enact(self):
        if self.enacted:
            return
        self.enacted = True
        if self.quorum.sig_valid(self.document.identity.key):
            self.document.subscribers.add(self.subscriber.key)
            if self.owner:
                self.quorum.transmit_complete(self.document)

    def update(self):
        if self.quorum.done:
            self.enact()

    def transmit(self):
        self.owner.lock_action(self.document, {
            'type': 'deje-subscribe',
            'subscriber': self.subscriber.location,
        })
        self.quorum.transmit(self.document)
        self.update()

    @property
    def version(self):
        return None

    @property
    def hashcontent(self):
        return self.subscriber.key

    def hash(self):
        return self.quorum.hash

    @property
    def author(self):
        return self.subscriber

    @property
    def owner(self):
        return self.document.owner
