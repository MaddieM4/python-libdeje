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

class Animus(object):
    def __init__(self, document, auto_activate = True):
        self.document = document
        self.interpreter = None
        if auto_activate:
            self.activate()

    # Callbacks

    def on_resource_update(self, path, propname, oldpath=None):
        if self.activate():
            self.interpreter.on_resource_update(path, propname, oldpath)

    def on_checkpoint_achieve(self, cp, author):
        if self.activate():
            self.interpreter.on_checkpoint_achieve(cp, author)

    def checkpoint_test(self, cp, author):
        if self.activate():
            return self.interpreter.checkpoint_test(cp, author)

    def quorum_participants(self):
        if self.activate():
            return self.interpreter.quorum_participants()

    def quorum_thresholds(self):
        if self.activate():
            return self.interpreter.quorum_thresholds()

    def can_read(self, ident):
        if self.activate():
            return self.interpreter.can_read(ident)

    def can_write(self, ident):
        if self.activate():
            return self.interpreter.can_write(ident)

    def request_protocols(self):
        if self.activate():
            return self.interpreter.request_protocols()

    def host_request(self, callback, args):
        if self.activate():
            return self.interpreter.host_request(callback, args)

    # Handler

    @property
    def handler(self):
        return self.document.handler

    # Memory conservation

    def activate(self):
        if not self.ready and self.handler:
            self.interpreter = self.handler.interpreter()
        return self.ready

    def deactivate(self):
        self.interpreter = None

    @property
    def ready(self):
        return self.interpreter != None
