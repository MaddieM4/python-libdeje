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

import re

# Basic well-formedness

MSG_NOT_DICT = {
    'code': 30,
    'explanation':"Recieved non-{} message, dropping",
}

MSG_NO_TYPE = {
    'code': 31,
    'explanation':"Recieved message with no type, dropping",
}

MSG_UNKNOWN_TYPE = {
    'code': 32,
    'explanation':"Recieved message with unknown type (%r)",
} 

# Locking errors

# Permissions errors

PERMISSION_CANNOT_READ = {
    'code': 50,
    'explanation': "Permissions error: cannot read",
}

PERMISSION_CANNOT_WRITE = {
    'code': 51,
    'explanation': "Permissions error: cannot write",
}

PERMISSION_DOCINFO_NOT_PARTICIPANT = {
    'code': 52,
    'explanation': "%r information came from non-participant source, ignoring",
}

# Event errors

# Subscription errors

option_pattern = re.compile('^[A-Z_]+$')
def get_options():
    g = globals()
    return dict(
        (name, g[name])
        for name in g.keys()
        if option_pattern.match(name)
    )

def lookup(code):
    for option in get_options().values():
        if option['code'] == code:
            return option
    raise IndexError("No error known for code %d" % code)
