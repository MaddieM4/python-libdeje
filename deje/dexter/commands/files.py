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

from __future__ import absolute_import

from deje.dexter.commands.group import DexterCommandGroup

class DexterCommandsFiles(DexterCommandGroup):

    def do_fwrite(self, args):
        '''
        Write contents of a view to a file.

        This command takes 1-2 arguments. The first argument, the
        file name, is mandatory. The second argument, the view name,
        is optional - by default, the current view will be written
        to the file.
        '''
        if len(args) < 1 or len(args) > 2:
            self.output("fwrite takes 1-2 args, got %d" % len(args))
            return

        filename = args[0]
        if len(args) == 1:
            viewname = self.interface.cur_view
        else:
            viewname = args[1]

        try:
            with open(filename, 'w') as thefile:
                view = self.interface.get_view(viewname)
                thefile.write('\n'.join(view.contents))
        except IOError as e:
            self.output('IOError %d: %s' % (e.errno, e.strerror))
            return
        self.output("Wrote view %s to file %s" % (viewname, filename))
