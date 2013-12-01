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

    def verify_args(self, args, name):
        if len(args) < 1 or len(args) > 2:
            self.output("%s takes 1-2 args, got %d" % (name, len(args)) )
            return (None, None)

        filename = args[0]
        if len(args) == 1:
            viewname = self.interface.cur_view
        else:
            viewname = args[1]

        return filename, viewname

    def do_fwrite(self, args):
        '''
        Write contents of a view to a file.

        This command takes 1-2 arguments. The first argument, the
        file name, is mandatory. The second argument, the view name,
        is optional - by default, the current view will be written
        to the file.
        '''
        filename, viewname = self.verify_args(args, 'fwrite')
        if not filename:
            return
        try:
            with open(filename, 'w') as thefile:
                view = self.interface.get_view(viewname)
                thefile.write('\n'.join(view.contents))
        except IOError as e:
            self.output('IOError %d: %s' % (e.errno, e.strerror))
            return
        self.output("Wrote view %s to file %s" % (viewname, filename))

    def do_fread(self, args):
        '''
        Read contents of a file as a series of commands.

        This command takes 1-2 arguments. The first argument, the
        file name, is mandatory. The second argument, the view name,
        is optional - by default, the current view will be used as
        the context to execute the commands.

        If you specify a view name, the interface will switch to that
        view before executing the commands.
        '''
        filename, viewname = self.verify_args(args, 'fread')
        if not filename:
            return

        try:
            thefile = open(filename, 'r')
        except IOError as e:
            self.output('IOError %d: %s' % (e.errno, e.strerror))
            return

        self.interface.cur_view = viewname
        try:
            for line in thefile:
                self.interface.do_command(line.strip())
        finally:
            thefile.close()
