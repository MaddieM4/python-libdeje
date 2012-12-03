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

class Quorum(object):
    def __init__(self, document, version, content, threshold = "write", signatures = {}):
        self.document   = document
        self.version    = version
        self.content    = content
        self.threshtype = threshold
        self.signatures = dict({})

    def sig_valid(self, author):
        identity, signature = self.signatures[author]
        return validate_signature(identity, self.hash, signature)

    def sign(self, identity, signature = None, duration = DEFAULT_DURATION):
        if not signature:
            signature = generate_signature(identity, self.hash, duration)
        self.signatures[identity.name] = (identity, signature)

    @property
    def completion(self):
        '''
        >>> import testing
        >>> quorum = testing.quorum()
        >>> ident  = testing.identity()

        >>> quorum.completion
        0
        >>> quorum.sign(ident)
        >>> quorum.completion
        1
        '''
        return len(self.valid_signatures)

    @property
    def done(self):
        return self.completion >= self.threshold

    @property
    def outdated(self):
        '''
        >>> import testing;
        >>> cp = testing.checkpoint( testing.document(handler_lua_template="echo_chamber") )
        >>> ident = testing.identity()
        >>> quorum = cp.quorum

        >>> quorum.document.version
        0
        >>> quorum.version
        0
        >>> quorum.outdated
        False
        >>> quorum.sign(ident)
        >>> quorum.outdated
        False
        >>> cp.enact()
        Checkpoint '{'x': 'y'}' achieved.
        >>> quorum.document.version
        1
        >>> quorum.version
        0
        >>> quorum.outdated
        True
        '''
        return self.document.version > self.version

    @property
    def participants(self):
        '''
        >>> import testing
        >>> quorum = testing.quorum()
        >>> quorum.participants
        [u'anonymous']
        '''
        return self.document.get_participants()

    @property
    def thresholds(self):
        return self.document.get_thresholds()

    @property
    def threshold(self):
        return self.thresholds[self.threshtype]

    @property
    def valid_signatures(self):
        return [ x for x in self.signatures if self.sig_valid(x) ]

    @property
    def hash(self):
        return checksum(self.content)

def validate_signature(identity, content_hash, signature):
    if type(identity) in (str, unicode, bytes):
        raise ValueError("Identity lookups not available at this time.")
    try:
        expires, subsig = signature.split("\x00", 1)
    except:
        # Bad signature format
        return False
    expire_date = datetime.datetime.strptime(expires, "%Y-%m-%d %H:%M:%S.%f")
    plaintext = expires + content_hash
    return (expire_date > datetime.datetime.utcnow()) and identity.verify_signature(subsig, plaintext)

def generate_signature(identity, content_hash, duration = DEFAULT_DURATION):
    if type(identity) in (str, unicode, bytes):
        raise ValueError("Identity lookups not available at this time.")
    expires = (datetime.datetime.utcnow() + duration).isoformat(' ')
    return expires + "\x00" + identity.sign(expires + content_hash)
