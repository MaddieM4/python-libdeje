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
import datetime

DEFAULT_DURATION = datetime.timedelta(minutes = 5)

class Checkpoint(object):
    def __init__(self, content, version, author = None, signatures = {}):
        self.content = content
        self.signatures = dict(signatures)
        self.version = int(version)
        self.author = author

    def enact(self, document):
        document.animus.on_checkpoint_achieve(self.content, self.author)

    def test(self, document):
        return document.animus.checkpoint_test(self.content, self.author)

    def hash(self):
        return checksum([self.content, self.author])

    def sign(self, identity, duration = DEFAULT_DURATION):
        expires = (datetime.datetime.utcnow() + duration).isoformat(' ')
        return expires + "\x00" + identity.sign(expires + self.hash())
