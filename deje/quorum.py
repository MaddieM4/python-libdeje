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

import datetime
from persei import *

from ejtp.identity import Identity
from ejtp.util.hasher import checksum

DEFAULT_DURATION = datetime.timedelta(minutes = 5)

class Quorum(object):
    def __init__(self, parent, threshold = "write", signatures = {}):
        self.parent     = parent
        self.threshtype = threshold
        self.signatures = {}
        self.document._qs.register(self)
        self.transmitted_complete = False
        for identity in signatures:
            self.sign(identity, signatures[identity])

    def sig_valid(self, key):
        if key not in self.signatures:
            return False
        identity, signature = self.signatures[key]
        return (identity in self.participants) and validate_signature(identity, self.hash, signature)

    def sign(self, identity, signature = None, duration = DEFAULT_DURATION):
        if not signature:
            signature = generate_signature(identity, self.hash, duration)
        assert_valid_signature(identity, self.hash, signature)
        # Equivalent or updated signature or non-colliding read.
        # Don't check for collisions in QS
        if self.sig_valid(identity.key) or self.threshtype == "read":
            self.signatures[identity.key] = (identity, signature)
            return

        with self.document._qs.transaction(identity, self):
            self.signatures[identity.key] = (identity, signature)

    def clear(self):
        """
        Clear out all signatures.
        """
        self.signatures = {}

    def transmit(self, signatures = None):
        '''
        Send a deje-lock-acquired for every valid signature
        '''
        signers = signatures or self.valid_signatures
        for signer in signers:
            self.document.owner.transmit(
                self.document,
                "deje-lock-acquired",
                {
                    'signer' : signer,
                    'content-hash' : self.hash,
                    'signature': self.transmittable_sig(signer),
                },
                [self.parent.author.key],
                participants = True # includes all signers
            )

    def transmit_complete(self):
        '''
        Send a deje-lock-complete with all valid signatures
        '''
        if self.transmitted_complete:
            return

        self.transmitted_complete = True

        self.document.owner.transmit(
            self.document,
            "deje-lock-complete",
            {
                'signatures' : self.sigs_dict(),
                'content-hash' : self.hash,
            },
            [self.parent.author.key],
            participants = True # includes all signers
        )

    def transmittable_sig(self, signer):
        return self.signatures[signer][1]

    def sigs_dict(self):
        sigs = {}
        for signer in self.valid_signatures:
            sigs[signer] = self.transmittable_sig(signer)
        return sigs

    # Parent-derived properties

    @property
    def document(self):
        return self.parent.document

    @property
    def version(self):
        return self.parent.version

    @property
    def content(self):
        return self.parent.hashcontent

    # Handler-derived properties

    @property
    def completion(self):
        return len(self.valid_signatures)

    @property
    def competing(self):
        return not (self.done or self.outdated)

    @property
    def done(self):
        return self.completion >= self.threshold

    @property
    def outdated(self):
        # Version is not relevant for read requests
        if self.version != None:
            return self.document.version != self.version
        else:
            return False

    @property
    def participants(self):
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
    try:
        assert_valid_signature(identity, content_hash, signature)
        return True
    except:
        return False

def assert_valid_signature(identity, content_hash, signature):
    if not isinstance(identity, Identity):
        raise TypeError("Expected ejtp.identity.core.Identity, got %r" % identity)
    try:
        expires, subsig = signature.split("\x00", 1)
    except:
        raise ValueError("Bad signature format - no nullbyte separator")
    expire_date = datetime.datetime.strptime(String(expires).export(), "%Y-%m-%d %H:%M:%S.%f")
    plaintext = expires + content_hash
    if not expire_date > datetime.datetime.utcnow():
        raise ValueError("Signature is expired")
    if not identity.verify_signature(subsig, plaintext):
        raise ValueError("Identity object thinks sig is not valid")

def generate_signature(identity, content_hash, duration = DEFAULT_DURATION):
    if not isinstance(identity, Identity):
        raise TypeError("Expected ejtp.identity.core.Identity, got %r" % identity)
    expires = RawData((datetime.datetime.utcnow() + duration).isoformat(' '))
    return expires + RawData((0,)) + identity.sign(expires + content_hash)
