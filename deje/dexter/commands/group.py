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

class DexterVisibleError(ValueError):
    def __str__(self):
        return '\n'.join(str(x) for x in self.args)

class DexterCommandGroup(object):
    def __init__(self, parent):
        self.parent = parent

    def get_vars(self, *names):
        result = {}
        for name in names:
            result[name] = self.interface.data[name]
        return result

    def verify_num_args(self, name, num, min, max):
        if min == None:
            msg = '%s takes up to %d arg(s), got %d' % \
                (name, max, num)
            if num > max:
                self.fail(msg)
        elif max == None:
            msg = '%s takes at least %d arg(s), got %d' % \
                (name, min, num)
            if num < min:
                self.fail(msg)
        elif min == max:
            msg = '%s takes exactly %d arg(s), got %d' % \
                (name, min, num)
            if num != min:
                self.fail(msg)
        else:
            msg = '%s takes %d-%d arg(s), got %d' % \
                (name, min, max, num)
            if num > max or num < min:
                self.fail(msg)

    def fwrite(self, filename, contents):
        try:
            with open(filename, 'w') as thefile:
                thefile.write(contents)
        except IOError as e:
            self.fail('IOError %d: %s' % (e.errno, e.strerror))

    def fread(self, filename):
        try:
            with open(filename, 'r') as thefile:
                return thefile.read()
        except IOError as e:
            self.fail('IOError %d: %s' % (e.errno, e.strerror))

    def fail(self, *args):
        raise DexterVisibleError(*args)

    @property
    def interface(self):
        return self.parent.interface

    @property
    def output(self):
        return self.parent.output

    @property
    def get_description(self):
        return self.parent.get_description
