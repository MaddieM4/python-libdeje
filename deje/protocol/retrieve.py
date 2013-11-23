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

from __future__ import absolute_import
from persei import *

from deje.protocol.handler import ProtocolHandler

class RetrieveHandler(ProtocolHandler):

    def __init__(self, parent):
        ProtocolHandler.__init__(self, parent)
        self._on_events = RetrieveEventsHandler(self)
        self._on_state  = RetrieveStateHandler(self)

class RetrieveEventsHandler(ProtocolHandler):

    def _on_query(self, message):
        qid    = message.qid
        doc    = message.doc
        sender = self.owner.identities.find_by_location(message.sender)
        if not doc.can_read(sender):
            return self.owner.error(msg, errors.PERMISSION_CANNOT_READ)

        if 'start' in message:
            h = String(message['start'])
            try:
                start = doc._history.event_index_by_hash(h)
            except KeyError:
                return # TODO: Respond with error
        else:
            start = 0

        if 'end' in message:
            h = String(message['end'])
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

    def _on_response(self, message):
        qid    = message.qid
        doc    = message.doc
        sender = self.owner.identities.find_by_location(message.sender)
        if sender not in doc.get_participants():
            return self.owner.error(message.msg, errors.PERMISSION_DOCINFO_NOT_PARTICIPANT, "event")
        events  = message['events']

        doc.signals['recv-events'].send(
            self,
            qid=qid,
            events=events
        )

class RetrieveStateHandler(ProtocolHandler):

    def _on_query(self, message):
        qid    = message.qid
        doc    = message.doc
        sender = self.owner.identities.find_by_location(message.sender)
        if not doc.can_read(sender):
            return self.owner.error(message.msg, errors.PERMISSION_CANNOT_READ)
        version = message['version']
        state = doc._history.generate_state(version).serialize()
        self.owner.reply(
            doc,
            'deje-retrieve-state-response',
            {
                'qid'  : qid,
                'state': state,
            },
            sender.key
        )

    def _on_response(self, message):
        qid    = message.qid
        doc    = message.doc
        sender = self.owner.identities.find_by_location(message.sender)
        if sender not in doc.get_participants():
            return self.owner.error(message.msg, errors.PERMISSION_DOCINFO_NOT_PARTICIPANT, "state")
        state = message['state']
        doc.signals['recv-state'].send(
            self,
            qid=qid,
            state=state
        )
