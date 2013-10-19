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

DEFAULT_DURATION = datetime.timedelta(minutes = 5)

class Quorum(object):
    def __init__(self, action, qs = None, signatures = {}):
        self.action     = action
        self.qs         = qs
        self.signatures = {}
        self.transmitted_complete = False
        for identity in signatures:
            self.sign(identity, signatures[identity])
        if qs:
            qs.register(self)

    @property
    def threshtype(self):
        return self.action.quorum_threshold_type

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

        with self.qs.transaction(identity, self):
            self.signatures[identity.key] = (identity, signature)

    def clear(self):
        """
        Clear out all signatures.
        """
        self.signatures = {}

    def check_enact(self, document):
        '''
        Call self.enact() if self.action is ready.
        '''
        if self.done and not self.action.is_done(document):
            self.enact(document)

    def enact(self, document):
        '''
        Enact self.action and transmit completion afterwards.
        '''
        self.action.enact(self, document)
        if document.owner:
            self.transmit_complete(document)

    def transmit_action(self, document):
        '''
        Announce an action, and begin trying to collect a consensus.
        '''
        document.owner.lock_action(
            document,
            self.content
        )
        self.transmit(document)
        self.check_enact(document)

    def transmit(self, document, signatures = None):
        '''
        Send a deje-lock-acquired for every valid signature
        '''
        signers = signatures or self.valid_signatures
        for signer in signers:
            document.owner.transmit(
                document,
                "deje-lock-acquired",
                {
                    'signer' : signer,
                    'content-hash' : self.hash,
                    'signature': self.transmittable_sig(signer),
                },
                [self.action.author.key],
                participants = True # includes all signers
            )

    def transmit_complete(self, document):
        '''
        Send a deje-lock-complete with all valid signatures
        '''
        if self.transmitted_complete:
            return

        self.transmitted_complete = True

        document.owner.transmit(
            document,
            "deje-lock-complete",
            {
                'signatures' : self.sigs_dict(),
                'content-hash' : self.hash,
            },
            [self.action.author.key],
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
    def version(self):
        return self.action.version

    @property
    def content(self):
        return self.action.serialize()

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
        if self.threshtype == 'read':
            return False
        else:
            return self.qs.version != self.version

    @property
    def participants(self):
        if not self.qs:
            raise ValueError("Cannot determine participants without QS")
        return self.qs.participants

    @property
    def thresholds(self):
        if not self.qs:
            raise ValueError("Cannot determine thresholds without QS")
        return self.qs.thresholds

    @property
    def threshold(self):
        if not self.qs:
            raise ValueError("Cannot determine threshold without QS")
        return self.thresholds[self.threshtype]

    @property
    def valid_signatures(self):
        return [ x for x in self.signatures if self.sig_valid(x) ]

    @property
    def hash(self):
        return self.action.hash()

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
