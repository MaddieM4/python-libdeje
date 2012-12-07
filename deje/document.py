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

import animus
import quorumspace
from checkpoint import Checkpoint

class Document(object):
    def __init__(self, name, handler_path="/handler.lua", resources=[], owner = None):
        self._name = name
        self._handler = handler_path
        self._owner = owner
        self._resources = {}
        self._qs = quorumspace.QuorumSpace(self)
        self._animus = animus.Animus(self)
        self._blockchain = []
        for res in resources:
            self.add_resource(res)

    # High-level resource manipulation

    def add_resource(self, resource):
        self._animus.on_resource_update(resource.path, 'add')
        self._resources[resource.path] = resource
        resource.document = self

    def get_resource(self, path):
        return self._resources[path]

    def del_resource(self, path):
        self._animus.on_resource_update(path, 'delete')
        del self._resources[path]

    @property
    def resources(self):
        return self._resources

    # Animus

    def activate(self):
        self._animus.activate()

    def deactivate(self):
        self._animus.deactivate()

    @property
    def animus(self):
        return self._animus

    # Host requests

    def request(self, callback, *args):
        return self.animus.host_request(callback, args)

    # Checkpoint stuff

    def checkpoint(self, cp):
        "Create a checkpoint from arbitrary object 'cp'"
        if not self.can_write():
            raise ValueError("You don't have write permission")
        checkpoint = Checkpoint(self, cp, author = "anonymous")
        valid = checkpoint.test()
        if valid:
            if self.owner:
                checkpoint.quorum.sign(self.identity)
                self.owner.attempt_checkpoint(self, checkpoint)
            else:
                checkpoint.enact()
            return checkpoint
        else:
            raise ValueError("Checkpoint %r was not valid" % cp)

    @property
    def competing(self):
        "All competing quorums"
        return self._qs.get_competing_actions()

    # Handler-derived properties

    def get_participants(self):
        return self.animus.quorum_participants()

    def get_thresholds(self):
        return self.animus.quorum_thresholds()

    def get_request_protocols(self):
        return self.animus.request_protocols()

    def can_read(self, ident = None):
        ident = ident or self.identity
        return self.animus.can_read(ident)

    def can_write(self, ident = None):
        ident = ident or self.identity
        return self.animus.can_write(ident)

    # Handler

    @property
    def handler(self):
        if self._handler in self._resources:
            return self.get_resource(self._handler)
        else:
            return None

    def set_handler(self, path):
        self._handler = path

    # Other accessors

    @property
    def name(self):
        return self._name

    @property
    def owner(self):
        return self._owner

    @property
    def identity(self):
        if self.owner:
            return self.owner.identity
        else:
            return "anonymous"

    @property
    def version(self):
        return len(self._blockchain)
