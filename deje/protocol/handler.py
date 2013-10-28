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

from ejtp.identity import Identity

class ProtocolHandler(object):
    def __init__(self, parent):
        self.parent = parent

    @property
    def owner(self):
        return self.parent.owner

    @property
    def toplevel(self):
        return self.parent.toplevel

    def send(self, doc, ctype, content, target):
        self.owner.reply(doc, ctype, content, target)

    def write_json(self, address, content):
        self.owner.client.write_json(address, content)

    def identity(self, location):
        if isinstance(location, Identity):
            return location
        else:
            return self.owner.identities.find_by_location(location)
