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

from persei import *

exported_functions = (
    'get_resource',
    'get_ident',
    'clone_table',
    'event',
    'debug',
)

class SRFlag(object):
    def __init__(self):
        self.valid = True

    def revoke(self):
        self.valid = False

class API(object):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.queue = []

    @property
    def document(self):
        return self.interpreter.document

    def process_queue(self):
        while self.queue:
            self.queue.pop()()

    # Exported functions

    def get_resource(self, path):
        if self.document:
            return self.document.get_resource(path)
        elif path == self.interpreter.resource.path:
            return self.interpreter.resource
        else:
            raise KeyError("Resource could not be found by DEJE API")

    def get_ident(self):
        ident = self.document.identity
        return ident.name

    def clone_table(self, source, dest):
        if isinstance(source, list):
            for i in range(len(source)):
                dest[i] = source[i]
        else:
            for key in source:
                dest[key] = source[key]
        return dest

    def event(self, ev):
        self.queue.append(lambda: self.document.event(ev))

    def debug(self, *args):
        self.document.debug(args)

    # set_resource

    def set_resource(self, state=None):
        """
        Returns a set_resource function and a flag for marking it invalid when
        you're done using the function. Prevents handler abuses.
        """
        sr_flag = SRFlag()
        def callback(path, prop, value):
            if sr_flag.valid:
                self.queue.append(lambda: self._set_resource(path, prop, value, state))
            else:
                raise ValueError("Attempt to access set_resource in handler after invalidation")
        return callback, sr_flag

    def _set_resource(self, path, prop, value, state=None):
        container = state or self.document
        try:
            res = container.get_resource(path)
        except KeyError:
            from deje.resource import Resource
            res = Resource(path)
            container.add_resource(res)
        res.set_property(prop, value)

    # Function exporter

    def export(self):
        output = {}
        for key in exported_functions:
            output[key] = getattr(self, key)
        return output
