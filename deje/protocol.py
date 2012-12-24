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

import read
import checkpoint

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
            print "Recieved message with unknown type (%r)" % mtype

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
                cp.quorum.sign(self.owner.identity)
                cp.quorum.transmit([self.owner.identity.name])
        if ltype == "deje-subscribe":
            rr_subname = lcontent['subscriber']
            subscriber = self.owner.identities.find_by_name(rr_subname)
            rr = read.ReadRequest(doc, subscriber)
            if doc.can_read(subscriber):
                rr.sign(self.owner.identity)
                rr.update()

    def _on_deje_lock_acquired(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_name(content['signer'])
        try:
            cp = doc._qs.by_hash[content['content-hash']].parent
        except KeyError:
            print "Unknown checkpoint data, dropping"
            return
        sig = content['signature'].encode('raw_unicode_escape')
        cp.quorum.sign(sender, sig)
        cp.update()

    def _on_deje_lock_complete(self, msg, content, ctype, doc):
        try:
            quorum = doc._qs.by_hash[content['content-hash']]
        except KeyError:
            print "Unknown checkpoint data for complete, dropping (%r)" % content['content-hash']
            return
        for signer in content['signatures']:
            sender = self.owner.identities.find_by_name(signer)
            sig = content['signatures'][signer].encode('raw_unicode_escape')
            quorum.sign(sender, sig)
            quorum.parent.update()

    # Document information

    def _on_deje_get_version(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.addr)
        if not doc.can_read(sender):
            print "Permissions error: cannot read"
            return
        self.owner.reply(doc, 'deje-doc-version', {'version':doc.version}, sender)

    def _on_deje_doc_version(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.addr)
        if sender.name not in doc.get_participants():
            print "Version information came from non-participant source, ignoring"
            return
        version = content['version']
        doc.trigger_callback('recv-version', version)

    def _on_deje_get_block(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.addr)
        blocknumber = content['version']
        blockcp = doc._blockchain[blocknumber]
        block = {
            'author': blockcp.authorname,
            'content': blockcp.content,
            'version': blockcp.version,
            'signatures': blockcp.quorum.sigs_dict(),
        }
        if not doc.can_read(sender):
            print "Permissions error: cannot read"
            return
        self.owner.reply(doc, 'deje-doc-block', {'block':block}, sender)

    def _on_deje_doc_block(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.addr)
        if sender.name not in doc.get_participants():
            print "Block information came from non-participant source, ignoring"
            return
        block = content['block']
        version = block['version']
        doc.trigger_callback('recv-block-%d' % version, block)

    def _on_deje_get_snapshot(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.addr)
        version = content['version']
        if not doc.can_read(sender):
            print "Permissions error: cannot read"
            return
        self.owner.reply(doc, 'deje-doc-snapshot', {'version':version, 'snapshot':doc.snapshot(version)}, sender)

    def _on_deje_doc_snapshot(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.addr)
        if sender.name not in doc.get_participants():
            print "Snapshot information came from non-participant source, ignoring"
            return
        snapshot = content['snapshot']
        version  = content['version']
        doc.trigger_callback('recv-snapshot-%d' % version, snapshot)
