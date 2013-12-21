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

    def get_params(self, *params):
        result = {}
        for pname in params:
            result[pname] = self.interface.data[pname]
        return result

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
            params = self.get_params(
                'idcache',
                'identity',
                'docname',
                'docserialized'
            )
        except KeyError as e:
            return self.output('Need to set variable %r' % e.args[0])
        
        cache = IdentityCache()
        try:
            cache.deserialize(params['idcache'])
        except:
            return self.output('Could not deserialize data in idcache')

        try:
            ident = cache.find_by_location(params['identity'])
        except KeyError:
            loc_string = strict(params['identity']).export()
            return self.output('No identity in cache for ' + loc_string)

        owner = Owner(ident)
        owner.identities = cache
        owner.client.rcv_callback = self.on_ejtp

        self.write_json = owner.client.write_json
        owner.client.write_json = self.write_json_wrapped
        self.interface.owner = owner

        if type(params['docname']) != str:
            json_str = strict(params['docname']).export()
            return self.output('Not a valid docname: ' + json_str)

        doc = Document(params['docname'], owner=owner)
        self.interface.document = doc

        try:
            doc.deserialize(params['docserialized'])
        except Exception as e:
            return self.output('Failed to deserialize data:\n%r' % e)

        self.interface.deje_initialized = True

        self.output('DEJE initialized')

    @property
    def initialized(self):
        return hasattr(self.interface, 'deje_initialized')

    def do_dexport(self, args):
        '''
        Serialize the current document to disk.

        Takes one command-line arg, for the filename.

        Will fail if DEJE has not already been initialized
        with the dinit command.
        '''
        if not self.initialized:
            return self.output('DEJE not initialized, see dinit command')

        if len(args) != 1:
            return self.output('dexport command takes one argument (filename)')
        fname = args[0]

        # TODO: Defend against failures in serialization and io
        with open(fname, 'w') as f:
            json.dump(self.interface.document.serialize(), f)
