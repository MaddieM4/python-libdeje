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

class QuorumSpace(object):
    def __init__(self, document):
        self.document  = document
        self.by_author = {}
        self.by_hash = {}

    def on_sign(self, identity, quorum):
        self.by_author[identity]  = quorum

    def register(self, quorum):
        self.by_hash[quorum.hash] = quorum

    def get_competing_actions(self):
        "Get all read and write actions in QS"
        return [x.parent for x in self.by_hash.values() if x.competing]

    def get_known_actions(self):
        return [x.parent for x in self.by_hash.values()]

    def transaction(self, identity, quorum):
        return QSTransaction(self, identity, quorum)

    def is_free(self, identity):
        if not identity in self.by_author.keys():
            return True
        return not self.by_author[identity].competing

    def assert_free(self, identity):
        '''
        Raise error if slot isn't free.
        '''
        if not self.is_free(identity):
            raise QSDoubleSigning(identity, self.document)

class QSTransaction(object):
    '''
    Allows you to use the shorthand:

        with qs.transaction(identity, quorum):
            do_stuff()

    Which will abort if the slot is taken, and register the signature event
    with the QS regardless of the success of the code in the with block.
    '''
    def __init__(self, qs, identity, quorum):
        self.qs = qs
        self.identity = identity
        self.quorum = quorum

    def __enter__(self):
        self.qs.assert_free(self.identity)

    def __exit__(self, type, value, traceback):
        self.qs.on_sign(self.identity, self.quorum)

# No identity can sign more than one quorum at a time.
class QSDoubleSigning(ValueError): pass
