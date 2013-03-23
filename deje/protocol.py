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

from __future__ import print_function
from ejtp.util.py2and3 import *
from deje import read
from deje import checkpoint
from deje import errors

class Protocol(object):
    '''
    Implementation of the DEJE protocol, to get it out of owner.py.
    '''

    def __init__(self, owner):
        self.owner = owner

    def call(self, msg, content, mtype, doc):
        '''
        Find and call protocol function
        '''
        funcname = "_on_" + mtype.replace('-','_')
        if hasattr(self, funcname):
            func = getattr(self, funcname)
            func(msg, content, mtype, doc)
        else:
            self.owner.error(msg, errors.MSG_UNKNOWN_TYPE, mtype)

    # Error handling

    def _on_deje_error(self, msg, content, ctype, doc):
        sender = msg.sender
        try:
            sender = self.owner.identities.find_by_location(sender).name
        except KeyError:
            pass # No saved information on this ident
        print("Error from %r, code %d: %r" % (sender, content['code'], content['explanation']))

    # Locking mechanisms

    def _on_deje_lock_acquire(self, msg, content, ctype, doc):
        lcontent = content['content']
        ltype = lcontent['type']
        if ltype == "deje-checkpoint":
            cp_content = lcontent['checkpoint']
            cp_version = lcontent['version']
            cp_author  = lcontent['author']

            cp = checkpoint.Checkpoint(doc, cp_content, cp_version, cp_author)
            if doc.can_write(cp_author) and cp.test():
                # TODO: Error message for permissions failures and test failures
                cp.quorum.sign(self.owner.identity)
                cp.quorum.transmit([self.owner.identity.name])
        if ltype == "deje-subscribe":
            rr_subname = lcontent['subscriber']
            subscriber = self.owner.identities.find_by_name(rr_subname)
            rr = read.ReadRequest(doc, subscriber)
            if doc.can_read(subscriber):
                # TODO: Error message for permissions failures
                rr.sign(self.owner.identity)
                rr.update()

    def _on_deje_lock_acquired(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_name(content['signer'])
        content_hash = String(content['content-hash'])
        try:
            quorum = doc._qs.by_hash[content_hash]
        except KeyError:
            #return self.owner.error(msg, errors.LOCK_HASH_NOT_RECOGNIZED, {'attempted':content_hash,'available':repr(doc._qs.by_hash)})
            return self.owner.error(msg, errors.LOCK_HASH_NOT_RECOGNIZED, content_hash.export())
        sig = RawData(content['signature'])
        quorum.sign(sender, sig)
        quorum.parent.update()

    def _on_deje_lock_complete(self, msg, content, ctype, doc):
        content_hash = String(content['content-hash'])
        try:
            quorum = doc._qs.by_hash[content_hash]
        except KeyError:
            return self.owner.error(msg, errors.LOCK_HASH_NOT_RECOGNIZED, content_hash.export())
        for signer in content['signatures']:
            sender = self.owner.identities.find_by_name(signer)
            sig = RawData(content['signatures'][signer])
            quorum.sign(sender, sig)
            quorum.parent.update()

    # Document information

    def _on_deje_get_version(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.sender)
        if not doc.can_read(sender):
            return self.owner.error(msg, errors.PERMISSION_CANNOT_READ)
        self.owner.reply(doc, 'deje-doc-version', {'version':doc.version}, sender)

    def _on_deje_doc_version(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.sender)
        if sender.name not in doc.get_participants():
            return self.owner.error(msg, errors.PERMISSION_DOCINFO_NOT_PARTICIPANT, "version")
        version = content['version']
        doc.trigger_callback('recv-version', version)

    def _on_deje_get_block(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.sender)
        blocknumber = content['version']
        blockcp = doc._blockchain[blocknumber]
        block = {
            'author': blockcp.authorname,
            'content': blockcp.content,
            'version': blockcp.version,
            'signatures': blockcp.quorum.sigs_dict(),
        }
        if not doc.can_read(sender):
            return self.owner.error(msg, errors.PERMISSION_CANNOT_READ)
        self.owner.reply(doc, 'deje-doc-block', {'block':block}, sender)

    def _on_deje_doc_block(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.sender)
        if sender.name not in doc.get_participants():
            return self.owner.error(msg, errors.PERMISSION_DOCINFO_NOT_PARTICIPANT, "block")
        block = content['block']
        version = block['version']
        doc.trigger_callback('recv-block-%d' % version, block)

    def _on_deje_get_snapshot(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.sender)
        version = content['version']
        if not doc.can_read(sender):
            return self.owner.error(msg, errors.PERMISSION_CANNOT_READ)
        self.owner.reply(doc, 'deje-doc-snapshot', {'version':version, 'snapshot':doc.snapshot(version)}, sender)

    def _on_deje_doc_snapshot(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.sender)
        if sender.name not in doc.get_participants():
            return self.owner.error(msg, errors.PERMISSION_DOCINFO_NOT_PARTICIPANT, "snapshot")
        snapshot = content['snapshot']
        version  = content['version']
        doc.trigger_callback('recv-snapshot-%d' % version, snapshot)

    # Transport shortcuts

    def error(self, recipients, code, explanation="", data={}):
        for r in recipients:
            self.owner.client.write_json(r, {
                'type':'deje-error',
                'code':int(code),
                'explanation':str(explanation),
                'data':data,
            })
