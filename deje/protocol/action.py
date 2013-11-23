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
from deje.action import Action
from deje.read   import ReadRequest

class ActionHandler(ProtocolHandler):

    def _on_completion(self, message):
        '''
        Sent to the action author when an action succeeds.

        Usually sent by every quorum participant.
        '''
        action = message.action
        if message['success'] != True:
            return # TODO : Do something about failure
        if isinstance(action, ReadRequest):
            version = message['version']
            self.toplevel._on_response(action.unique, [version])
