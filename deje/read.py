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

import quorum

class ReadRequest(object):
    def __init__(self, document, subscriber=None):
        self.document = document
        self.subscriber = subscriber or document.identity
        self.quorum   = quorum.Quorum(
                            self,
                            "read",
                        )

    def enact(self):
        if self.quorum.sig_valid(self.document.identity):
            self.document.subscribers.add(self.subscriber)

    def update(self):
        if self.quorum.done:
            self.enact()

    def transmit(self):
        pass

    @property
    def version(self):
        return None

    @property
    def hashcontent(self):
        return self.subscriber.name

    def hash(self):
        return self.quorum.hash
