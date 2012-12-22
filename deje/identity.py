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

from   ejtp.address import *
import ejtp.crypto

class Identity(object):
    def __init__(self, name, encryptor, location = None):
        '''
        >>> ident = Identity("joe", ['rotate', 8])
        >>> ident.name
        'joe'
        >>> e =  ident.encryptor
        >>> e # doctest: +ELLIPSIS
        <ejtp.crypto.rotate.RotateEncryptor object at ...>
        >>> e == ident.encryptor # Make sure this is cached
        True
        >>> plaintext = "example"
        >>> sig = ident.sign(plaintext)
        >>> sig
        'H\\xd0P\\xd8\\x90V\\xc4wX9\\x82\\xa7\\x04\\xbd\\xa3Pw:\\xbaO\\x02\\x808\\x8d\\xa1\\xe0\\xc4\\xa4\\xc8\\xeeLT'
        >>> ident.verify_signature(sig, plaintext)
        True
        '''
        self._name = name
        self._encryptor = encryptor
        self._location = location

    def sign(self, plaintext):
        return self.encryptor.sign(plaintext)

    def verify_signature(self, signature, plaintext):
        return self.encryptor.sig_verify(plaintext, signature)

    @property
    def name(self):
        return self._name

    @property
    def encryptor(self):
        if type(self._encryptor) in (list, tuple):
            self._encryptor = ejtp.crypto.make(self._encryptor)
        return self._encryptor

    @property
    def location(self):
        if self._location:
            return self._location
        else:
            raise AttributeError("Identity location not set")

    @location.setter
    def location(self, value):
        self._location = value

class EncryptorCache(object):
    def __init__(self, source={}):
        self.cache = {}
        self.cache.update(source)

    def __getitem__(self, location):
        location = str_address(location)
        return self.cache[location].encryptor.proto()

    def __setitem__(self, location, value):
        location = str_address(location)
        self.cache[location] = value

    def __delitem__(self, location):
        location = str_address(location)
        del self.cache[location]

    def update_ident(self, ident):
        self[ident.location] = ident

    def find_by_name(self, name):
        for ident in self.cache.values():
            if ident.name == name:
                return ident
        raise KeyError(name)

    def find_by_location(self, location):
        location = str_address(location)
        return self.cache[location]

    def __repr__(self):
        return "<EncryptorCache %r>" % repr(self.cache)

def sync_caches(*caches):
    sync = {}
    for c in caches:
        sync.update(c.cache)
    for c in caches:
        c.cache.update(sync)
