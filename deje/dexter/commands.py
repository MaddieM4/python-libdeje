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

import shlex

class DexterCommands(object):
    def __init__(self, interface):
        self.interface = interface

    def do(self, cmdstr):
        args = self.get_args(cmdstr)
        if not len(args):
            return
        func = self.get_handler(args[0])
        if func != None:
            func(args[1:])
        else:
            self.interface.output('No such command: %r' % args[0])

    def get_args(self, cmdstr):
        return shlex.split(cmdstr)

    def get_handler(self, command):
        funcname  = 'do_' + command
        if hasattr(self, funcname):
            return getattr(self, funcname)
        else:
            return None

    def get_description(self, command):
        raw = getattr(self, 'do_' + command).__doc__
        if not raw:
            return ['No description available.']
        return [s.strip() for s in raw.strip().split('\n')]

    def do_quit(self, args):
        '''
        Exit the program.

        Does not save anything, and doesn't ask either.
        '''
        quit(0)

    def do_help(self, args):
        '''
        A simple little help message.

        You can also view full descriptions with "help commandname".
        '''
        if len(args):
            lines = self._do_help_with_args(args)
        else:
            lines = self._do_help_no_args()
        for line in lines:
            self.output(line)

    def _do_help_with_args(self, args):
        lines = []
        for command in args:
            try:
                desc = self.get_description(command)
            except:
                desc = ['No such command.']
            desc[0] = command + " :: " + desc[0]
            lines.extend(desc)
        return lines

    def _do_help_no_args(self):
        return [
            'Dexter is a low-level DEJE client.',
            'It\'s perfect for low-level management of documents.',
            'Type "commands" to see the list of available commands.',
            'Type "help somecommand" to see more about a command.',
        ]

    def do_commands(self, args):
        '''
        List all available commands.
        '''
        commands = [x[3:] for x in dir(self) if x.startswith('do_')]
        commands.sort()
        for command in commands:
            description = self.get_description(command)
            oneline     = description[0]
            self.output('%s :: %s' % (command, oneline))

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

    @property
    def output(self):
        return self.interface.output
