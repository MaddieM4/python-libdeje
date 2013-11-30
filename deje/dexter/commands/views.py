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

class DexterCommandsViews(DexterCommandGroup):

    def do_view(self, args):
        '''
        List views, or select one.

        Views are different distinct "terminals" within Dexter.
        For example, "msglog" displays all EJTP messages that
        arrive or are sent.

        You can execute commands in any view, but some commands
        may switch your view to show you the result of the
        operation. The current view is always displayed as part
        of the command prompt.

        When the "views" command is executed without arguments,
        it lists all available views. Use "view someview" to
        switch to the view called "someview". If it doesn't
        exist, it will be created.
        '''
        if len(args) == 0:
            lines = self._do_list_views()
        elif len(args) == 1:
            lines = self._do_switch_view(args[0])
        else:
            lines = ['"view" command takes, at most, 1 argument.']
        for line in lines:
            self.output(line)

    def _do_list_views(self):
        lines = []
        for name, view in self.interface.views.items():
            if view.desc:
                lines.append('%s :: %s' % (name, view.desc))
            else:
                lines.append(name)
        lines.sort()
        return lines

    def _do_switch_view(self, to_view):
        self.interface.cur_view = to_view
        return []
