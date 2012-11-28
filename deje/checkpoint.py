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
        '''
        >>> Checkpoint({'x':'y'}, 4, 'mick-and-bandit').hash()
        '960341d14e3531a50770bd6529a422d2b4997ae9'
        '''
        return checksum([self.content, self.version, self.author])

    def make_signature(self, identity, duration = DEFAULT_DURATION):
        expires = (datetime.datetime.utcnow() + duration).isoformat(' ')
        return expires + "\x00" + identity.sign(expires + self.hash())

    def verify_signature(self, identity, signature):
        try:
            expires, subsig = signature.split("\x00")
        except:
            return false
        plaintext = expires + self.hash()
        return identity.verify_signature(subsig, plaintext)

    def sign(self, identity, signature = None, duration = DEFAULT_DURATION):
        if type(identity) in (str, unicode):
            if not signature:
                raise ValueError("No signature provided, and could not derive from identity %r" % signature)
            identity_name = identity
        else:
            if signature:
                self.verify_signature(identity, signature) or raise ValueError("Invalid signature")
            else:
                signature = self.make_signature(identity, duration)
            identity_name = identity.name
        self.signatures[identity_name] = signature
