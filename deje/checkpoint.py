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

    def has_quorum(self, document):
        write_threshold = document.get_thresholds()['write']
        if len(self.signatures.keys()) >= write_threshold:
            return True
        else:
            return False

    def hash(self):
        '''
        >>> import testing
        >>> testing.checkpoint().hash()
        '960341d14e3531a50770bd6529a422d2b4997ae9'
        '''
        return checksum([self.content, self.version, self.author])

    def make_signature(self, identity, duration = DEFAULT_DURATION):
        '''
        >>> import testing
        >>> cp = testing.checkpoint()
        >>> ident = testing.identity()
        >>> sig = cp.make_signature(ident)
        >>> cp.verify_signature(ident, sig)
        True
        >>> cp.make_signature("some string")
        Traceback (most recent call last):
        ValueError: Identity lookups not available at this time.
        >>> cp.verify_signature("some string", sig)
        Traceback (most recent call last):
        ValueError: Identity lookups not available at this time.
        >>> cp.sign(ident)
        >>> cp.verify_signature(ident, cp.signatures[ident.name])
        True
        >>> cp.sign("anonymous")
        Traceback (most recent call last):
        ValueError: No signature provided, and could not derive from identity 'anonymous'
        '''
        if type(identity) in (str, unicode, bytes):
            raise ValueError("Identity lookups not available at this time.")
        expires = (datetime.datetime.utcnow() + duration).isoformat(' ')
        return expires + "\x00" + identity.sign(expires + self.hash())

    def verify_signature(self, identity, signature):
        if type(identity) in (str, unicode, bytes):
            raise ValueError("Identity lookups not available at this time.")
        try:
            expires, subsig = signature.split("\x00", 1)
        except:
            # Bad signature format
            return False
        expire_date = datetime.datetime.strptime(expires, "%Y-%m-%d %H:%M:%S.%f")
        plaintext = expires + self.hash()
        return (expire_date > datetime.datetime.utcnow()) and identity.verify_signature(subsig, plaintext)

    def sign(self, identity, signature = None, duration = DEFAULT_DURATION):
        if type(identity) in (str, unicode, bytes):
            # String identity
            if not signature:
                raise ValueError("No signature provided, and could not derive from identity %r" % identity)
            identity_name = identity
        else:
            # Identity object
            if signature:
                if not self.verify_signature(identity, signature):
                    raise ValueError("Invalid signature")
            else:
                signature = self.make_signature(identity, duration)
            identity_name = identity.name
        self.signatures[identity_name] = signature
