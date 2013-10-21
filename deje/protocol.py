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
from persei import *

from deje.quorum import Quorum
from deje.action import Action
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
        action = Action(lcontent, self.owner.identities).specific()
        quorum = doc._qs.get_quorum(action)
        if action.valid(doc):
            # TODO: Error message for validation failures
            quorum.sign(self.owner.identity)
            quorum.transmit(doc)
            quorum.check_enact(doc)

    def _on_deje_lock_acquired(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(content['signer'])
        action = Action(content['content'], self.owner.identities).specific()
        content_hash = String(action.hash())
        quorum = doc._qs.get_quorum(action)

        sig = RawData(content['signature'])
        quorum.sign(sender, sig)
        quorum.check_enact(doc)

    def _on_deje_lock_complete(self, msg, content, ctype, doc):
        action = Action(content['content'], self.owner.identities).specific()
        content_hash = String(action.hash())
        quorum = doc._qs.get_quorum(action)
        for signer in content['signatures']:
            sender = self.owner.identities.find_by_location(signer)
            sig = RawData(content['signatures'][signer])
            quorum.sign(sender, sig)
        quorum.check_enact(doc)

    # Document information

    def _on_deje_get_version(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.sender)
        if not doc.can_read(sender):
            return self.owner.error(msg, errors.PERMISSION_CANNOT_READ)
        self.owner.reply(doc, 'deje-doc-version', {'version':doc.version}, sender.key)

    def _on_deje_doc_version(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.sender)
        if sender not in doc.get_participants():
            return self.owner.error(msg, errors.PERMISSION_DOCINFO_NOT_PARTICIPANT, "version")
        version = content['version']
        doc.signals['recv-version'].send(self, version=version)

    def _on_deje_retrieve_events_query(self, msg, content, ctype, doc):
        qid    = int(content['qid'])
        sender = self.owner.identities.find_by_location(msg.sender)
        if not doc.can_read(sender):
            return self.owner.error(msg, errors.PERMISSION_CANNOT_READ)

        if 'start' in content:
            h = String(content['start'])
            try:
                start = doc._history.event_index_by_hash(h)
            except KeyError:
                return # TODO: Respond with error
        else:
            start = 0

        if 'end' in content:
            h = String(content['end'])
            try:
                end = doc._history.event_index_by_hash(h)
            except KeyError:
                return # TODO: Respond with error
        else:
            end = len(doc._history.events) - 1

        events = [x.serialize() for x in doc._history.events[start:end+1]]
        self.owner.reply(
            doc,
            'deje-retrieve-events-response',
            {
                'qid': qid,
                'events': events,
            },
            sender.key
        )

    def _on_deje_retrieve_events_response(self, msg, content, ctype, doc):
        qid    = int(content['qid'])
        sender = self.owner.identities.find_by_location(msg.sender)
        if sender not in doc.get_participants():
            return self.owner.error(msg, errors.PERMISSION_DOCINFO_NOT_PARTICIPANT, "block")
        events  = content['events']

        doc.signals['recv-events'].send(
            self,
            events=events,
            qid=qid
        )

    def _on_deje_get_snapshot(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.sender)
        version = content['version']
        if not doc.can_read(sender):
            return self.owner.error(msg, errors.PERMISSION_CANNOT_READ)
        self.owner.reply(doc, 'deje-doc-snapshot', {'version':version, 'snapshot':doc.snapshot(version)}, sender.key)

    def _on_deje_doc_snapshot(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(msg.sender)
        if sender not in doc.get_participants():
            return self.owner.error(msg, errors.PERMISSION_DOCINFO_NOT_PARTICIPANT, "snapshot")
        snapshot = content['snapshot']
        version  = content['version']
        doc.signals['recv-snapshot'].send(
            self,
            version=version,
            snapshot=snapshot
        )

    # Transport shortcuts

    def error(self, recipients, code, explanation="", data={}):
        for r in recipients:
            self.owner.client.write_json(r, {
                'type':'deje-error',
                'code':int(code),
                'explanation':str(explanation),
                'data':data,
            })
