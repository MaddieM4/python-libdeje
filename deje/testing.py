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

from deje.tests.identity import identity

def checkpoint(doc = None):
    from deje.checkpoint import Checkpoint
    if not doc:
        doc = document()
    return Checkpoint(doc, {'x':'y'}, 0, 'mick-and-bandit')

def handler_lua(source):
    return document(handler_lua = source)

def document(name="testing", handler_lua = None, handler_lua_template = None):
    from deje.document import Document
    from deje.resource import Resource
    doc = Document(name)
    if handler_lua_template:
        import deje.handlers.lua as handlers
        handler_lua = getattr(handlers, handler_lua_template)()
    if handler_lua:
        handler = Resource('/handler.lua', handler_lua, 'The primary handler', 'text/lua')
        doc.add_resource(handler)
    return doc

def quorum():
    doc = document(handler_lua_template="echo_chamber")
    cp  = checkpoint(doc)
    return cp.quorum

def owner(ident = None):
    from deje.owner import Owner
    return Owner(ident or identity(), make_jack=False)

def ejtp_test():
    from ejtp.router import Router
    from deje.owner import Owner
    r = Router()
    mitzi  = Owner(identity("mitzi"),  r)
    atlas  = Owner(identity("atlas"),  r)
    victor = Owner(identity("victor"), r)
    mitzi.identities.sync(
        atlas.identities,
        victor.identities,
    )

    # Document that mitzi and atlas are part of, but victor is not.
    # Separate identical starting points for all of them.
    mdoc = document(handler_lua_template="tag_team")
    adoc = document(handler_lua_template="tag_team")
    vdoc = document(handler_lua_template="tag_team")
    mitzi.own_document(mdoc)
    atlas.own_document(adoc)
    victor.own_document(vdoc)
    return (mitzi, atlas, victor, mdoc, adoc, vdoc)
