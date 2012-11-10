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

    # Getters and setters

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, newpath):
        if type(newpath) in (str, unicode):
            if hasattr(self, '_path'):
                oldpath = self.path
                self._path = newpath
                self.trigger_change('path', oldpath=oldpath)
            else:
                self._path = newpath
        else:
            raise TypeError("Resource.path must be str or unicode, got %r", type(newpath))

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, newtype):
        if type(newtype) in (str, unicode):
            # TODO: Verify MIME validity
            self._type = newtype
            self.trigger_change('type')
        else:
            raise TypeError("Resource.type must be str or unicode, got %r", type(newtype))

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, newcontent):
        self._content = newcontent
        self.trigger_change('content')

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, newcomment):
        if type(newcomment) in (str, unicode):
            self._comment = newcomment
            self.trigger_change('comment')
        else:
            raise TypeError("Resource.comment must be str or unicode, got %r", type(newcomment))

    def trigger_change(self, propname, oldpath=None):
        if hasattr(self, 'document') and self.document:
            self.document.animus.on_resource_update(self.path, propname, oldpath or self.path)

    # Methods

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
