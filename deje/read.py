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

import quorum

class ReadRequest(object):
    def __init__(self, document, reply_to=None):
        self.document = document
        self.reply_to = reply_to or document.identity
        self.quorum   = quorum.Quorum(
                            self,
                            "read",
                        )

    @property
    def version(self):
        return None

    @property
    def hashcontent(self):
        return self.reply_to

    def hash(self):
        return self.quorum.hash
