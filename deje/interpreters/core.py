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

from sandbox import Sandbox

class Interpreter(object):
    def __init__(self, resource):
        self.resource = resource
        self.sandbox = Sandbox()
        self._context = None
        self.make_context()

    def make_context(self):
        raise NotImplementedError('Interpreter.make_context')

    def _context_call(self, *args):
        raise NotImplementedError('Interpreter._context_call')

    def _context_eval(self, *args):
        raise NotImplementedError('Interpreter._context_eval')

    def call(self, *args):
        return self.sandbox.call(self._context_call, *args)

    def eval(self, *args):
        return self.sandbox.call(self._context_eval, *args)

    @property
    def content(self):
        return self.resource.content
