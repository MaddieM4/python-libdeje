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

class Checkpoint(object):
    def __init__(self, document, content, version = None, author = None, signatures = {}):
        '''
        >>> from deje import testing
        >>> doc = testing.document(handler_lua_template="echo_chamber")
        >>> owner = testing.owner()
        >>> owner.own_document(doc)
        >>> cp = testing.checkpoint(doc)
        >>> ident = testing.identity()
        >>> cp.version
        0

        >>> cp.quorum.sign(ident)
        >>> cp.quorum.participants #doctest: +ELLIPSIS
        [...'mitzi@lackadaisy.com']
        >>> cp.quorum.sig_valid(ident.name)
        True
        >>> cp.quorum.sign("some string")
        Traceback (most recent call last):
        ValueError: Identity lookups not available at this time.
        >>> cp.quorum.sig_valid("some string")
        False
        '''
        self.document = document
        self.content  = content
        self.version  = int(version or self.document.version)
        self.author   = author
        self.enacted  = False
        self.quorum   = quorum.Quorum(
                            self,
                            signatures = signatures,
                        )
    def enact(self):
        if self.enacted:
            return
        self.enacted = True
        self.document._blockchain.append(self)
        self.document.animus.on_checkpoint_achieve(self.content, self.author)
        if self.owner:
            self.quorum.transmit_complete()

    def update(self):
        if self.quorum.done:
            self.enact()

    def transmit(self):
        self.owner.lock_action(self.document, {
            'type': 'deje-checkpoint',
            'version': self.version,
            'checkpoint': self.content,
            'author': self.authorname,
        })
        self.quorum.transmit()
        self.update()

    def test(self):
        return self.document.animus.checkpoint_test(self.content, self.author)

    @property
    def authorname(self):
        '''
        >>> from deje import testing
        >>> doc = testing.document(handler_lua_template="echo_chamber")
        >>> owner = testing.owner()
        >>> owner.own_document(doc)
        >>> cp = Checkpoint(doc, None, author=owner.identity)
        
        >>> cp.author #doctest: +ELLIPSIS
        <ejtp.identity.core.Identity object at ...>

        >>> cp.authorname
        'mitzi@lackadaisy.com'
        >>> doc.identity.name
        'mitzi@lackadaisy.com'
        '''
        return (hasattr(self.author, "name") and self.author.name) or self.author
        
    @property
    def hashcontent(self):
        return [self.content, self.version, self.authorname]

    def hash(self):
        '''
        >>> from deje import testing
        >>> testing.checkpoint().hash()
        String('a6aa316b4b784fda1a38b53730d1a7698c3c1a33')
        '''
        return self.quorum.hash

    @property
    def owner(self):
        return self.document.owner

def from_hashcontent(document, hashcontent, signatures={}):
    if type(hashcontent) != list or len(hashcontent) != 3:
        raise TypeError("checkpoint.from_hashcontent expects a list of length 3, got %r" % hashcontent)
    return Checkpoint(document, content, version, author, signatures)
