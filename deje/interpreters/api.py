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

exported_functions = (
    'get_resource',
    'get_ident',
    'checkpoint',
    'debug',
)

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
        return "anonymous"

    def checkpoint(self, cp):
        self.queue.append(lambda: self.document.checkpoint(cp))

    def debug(self, *args):
        for arg in args:
            print arg

    # Function exporter

    def export(self):
        output = {}
        for key in exported_functions:
            output[key] = getattr(self, key)
        return output
