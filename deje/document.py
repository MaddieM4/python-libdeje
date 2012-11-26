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

class Document(object):
    def __init__(self, handler_path="/handler.lua", resources=[]):
        self._handler = handler_path
        self._resources = {}
        self._animus = animus.Animus(self)
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

    # Checkpoint stuff

    def checkpoint(self, cp):
        "Create a checkpoint from arbitrary object 'cp'"
        valid = self.animus.checkpoint_test(cp) # TODO: store results
        print "Tested checkpoint %r and got result %r" % (cp, valid)
        if valid:
            self.animus.on_checkpoint_achieve(cp)

    # Handler

    @property
    def handler(self):
        if self._handler in self._resources:
            return self.get_resource(self._handler)
        else:
            return None

    def set_handler(self, path):
        self._handler = path
