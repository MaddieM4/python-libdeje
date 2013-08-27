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

from deje.resource import Resource

exported_functions = (
    'get_resource',
    'get_ident',
    'event',
    'debug',
)

class SRFlag(object):
    def __init__(self):
        self.valid = True

    def revoke(self):
        self.valid = False

class API(object):
    def __init__(self, document):
        self.document = document
        self.queue = []

    def process_queue(self):
        while self.queue:
            self.queue.pop()()

    # Exported functions

    def get_resource(self, path):
        return self.document.get_resource(path)

    def get_ident(self):
        ident = self.document.identity
        return ident.location

    def event(self, ev):
        self.queue.append(lambda: self.document.event(ev))

    def debug(self, *args):
        for arg in args:
            print(arg)

    # set_resource

    def set_resource(self):
        """
        Returns a set_resource function and a flag for marking it invalid when
        you're done using the function. Prevents handler abuses.
        """
        sr_flag = SRFlag()
        def callback(path, prop, value):
            if sr_flag.valid:
                self.queue.append(lambda: self._set_resource(path, prop, value))
            else:
                raise ValueError("Attempt to access set_resource in handler after invalidation")
        return callback, sr_flag

    def _set_resource(self, path, prop, value):
        try:
            res = self.document.get_resource(path)
        except KeyError:
            res = Resource(path)
            self.document.add_resource(res)
        res.set_property(prop, value)

    # Function exporter

    def export(self):
        output = {}
        for key in exported_functions:
            output[key] = getattr(self, key)
        return output
