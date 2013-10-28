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

from deje.action import Action

class ReadRequest(Action):
    def __init__(self, author):
        self.deserialize({
            'type'    : 'get_version',
            'author'  : author,
        })
        self.done = False

    @property
    def version(self):
        return None

    @property
    def quorum_threshold_type(self):
        return "read"

    def is_done(self, document):
        '''
        Returns whether Request has already been granted.
        '''
        return self.done

    def enact(self, quorum, document):
        '''
        Add subscriber to list.
        '''
        self.done = True

    def test(self, state):
        '''
        Read events are always valid.
        '''
        return True
