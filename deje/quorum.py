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

class Quorum(object):
    def __init__(self, document, threshold = "write", signatures = {}):
        self.document   = document
        self.threshtype = threshold
        self.signatures = dict({})

    def sig_valid(self, author):
        pass

    @property
    def completion(self):
        return len(self.valid_signatures)

    @property
    def done(self):
        return self.completion >= self.threshold

    @property
    def participants(self):
        return self.document.get_participants()

    @property
    def thresholds(self):
        return self.document.get_thresholds()

    @property
    def threshold(self):
        return self.thresholds[self.threshtype]

    @property
    def valid_signatures(self):
        return { x for x in self.signatures if self.sig_valid(x) }
