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

class Resource(object):
    def __init__(self, path="/", content="", comment="", type="application/x-octet-stream", source=None):
        if source:
            self.deserialize(source)
        else:
            self.path = path
            self.type = type
            self.content = content
            self.comment = comment
        self.document = None

    def interpreter(self):
        "Produce an interpreter object based on resource type."
        if self.type == "text/javascript":
            from interpreters import js
            return js.JSInterpreter(self)
        elif self.type == "text/lua":
            from interpreters import lua
            return lua.LuaInterpreter(self)
        else:
            raise TypeError("No interpreter for resource type " + str(self.type))

    def deserialize(self, source):
        for propname in ('path','type','content','comment'):
            if propname in source:
                setattr(self, propname, source[propname])

    def serialize(self):
        return {
            'path': self.path,
            'type': self.type,
            'content': self.content,
            'comment': self.comment,
        }
