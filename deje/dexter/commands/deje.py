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

import json

from ejtp.util.hasher import strict
from ejtp.identity    import IdentityCache
from deje.owner       import Owner
from deje.document    import Document

from deje.event       import Event
from deje.read        import ReadRequest

from deje.dexter.commands.group import DexterCommandGroup

class DexterCommandsDEJE(DexterCommandGroup):

    def on_ejtp(self, msg, client):
        try:
            msg_type = msg.unpack()['type']
        except:
            msg_type = "<could not parse>"

        logline = "%s : %s" % (strict(msg.sender).export(), msg_type)
        self.interface.output(logline, 'msglog')
        self.interface.owner.on_ejtp(msg, client)

    def write_json_wrapped(self, addr, data, wrap_sender = True):
        if type(data) == dict and 'type' in data:
            msg_type = data['type']
        else:
            msg_type = "<msg type not provided>"

        logline = '%s (ME) : %s' % (
            self.interface.owner.identity.key.export(),
            msg_type
        )
        self.interface.output(logline, 'msglog')
        self.write_json(addr, data, wrap_sender)

    def do_dinit(self, args):
        '''
        Initialize DEJE interactivity.

        This command must be used before any of the other d*
        commands. It reads from a few of the values in variable
        storage as initialization parameters:

        * idcache - EJTP identity cache
        * identity - location of EJTP identity in cache
        * docname - Name of the document for network sync
        * docserialized - serialized version of document

        The dinit command can be run more than once, but it's
        a bit of a reset, and may cause data loss in the
        stateful parts of the protocol. But it's also the only
        way to update the parameters used by the DEJE code -
        for example, any changes to the 'idcache' variable after
        initialization will have no effect.
        '''
        try:
            params = self.get_vars(
                'idcache',
                'identity',
                'docname',
                'docserialized'
            )
        except KeyError as e:
            self.fail('Need to set variable %r' % e.args[0])
        
        cache = IdentityCache()
        try:
            cache.deserialize(params['idcache'])
        except:
            self.fail('Could not deserialize data in idcache')

        try:
            ident = cache.find_by_location(params['identity'])
        except KeyError:
            loc_string = strict(params['identity']).export()
            self.fail('No identity in cache for ' + loc_string)

        owner = Owner(ident)
        owner.identities = cache
        owner.client.rcv_callback = self.on_ejtp

        self.write_json = owner.client.write_json
        owner.client.write_json = self.write_json_wrapped

        if type(params['docname']) != str:
            json_str = strict(params['docname']).export()
            self.fail('Not a valid docname: ' + json_str)

        doc = Document(params['docname'], owner=owner)

        try:
            doc.deserialize(params['docserialized'])
        except Exception as e:
            self.fail('Failed to deserialize data:\n%r' % e)

        # Wait until everything that could fail has gone right
        self.interface.owner = owner
        self.interface.document = doc
        self.output('DEJE initialized')

    @property
    def initialized(self):
        return hasattr(self.interface, 'document')

    def req_init(self):
        if not self.initialized:
            self.fail('DEJE not initialized, see dinit command')

    def do_devent(self, args):
        '''
        Propose a change to the document.

        Sends an Event action to the participants in
        this document, and prints progress, success,
        and failure to the 'doc' view as such updates
        are received.

        Takes one argument, the name of the variable
        containing the event contents. This must be a
        top-level variable.

        Will fail if DEJE has not already been initialized
        with the dinit command.
        '''
        self.req_init()
        self.verify_num_args('devent', len(args), 1, 1)

        vname  = args[0]
        if not vname in self.interface.data:
            self.fail("No such variable %r" % vname)

        content = self.interface.data[vname]
        self.interface.document.event(content)

    def do_dget_latest(self, args):
        '''
        Get the latest version number of the doc.

        This puts in a Read action to the participants
        in the document, and will print the result to
        the 'doc' view.

        Will fail if DEJE has not already been initialized
        with the dinit command.
        '''
        self.req_init()
        def callback(version):
            self.output('Document latest version is %r' % version, 'doc')

        doc = self.interface.document
        action = doc.get_version(callback)

    def do_dvexport(self, args):
        '''
        Serialize the current document to variable storage.

        Takes one command-line arg, for the var name.
        Cannot store deep into the variable tree.

        Will fail if DEJE has not already been initialized
        with the dinit command.
        '''
        self.req_init()
        self.verify_num_args('dvexport', len(args), 1, 1)

        vname  = args[0]
        serial = self.interface.document.serialize()
        self.interface.data[vname] = serial

    def do_dexport(self, args):
        '''
        Serialize the current document to disk.

        Takes one command-line arg, for the filename.

        Will fail if DEJE has not already been initialized
        with the dinit command.
        '''
        self.req_init()
        self.verify_num_args('dexport', len(args), 1, 1)

        fname = args[0]
        self.fwrite(
            fname,
            json.dumps(self.interface.document.serialize())
        )
