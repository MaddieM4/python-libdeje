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

# Prebaked handlers for Lua interpreter

def echo_chamber():
    '''
    Diagnostic, prints stuff on events.

    >>> doc = test_bootstrap(echo_chamber())
    >>> doc.activate()
    on_load
    >>> doc.update_scratch("joe", "marzipan")
    on_scratch_update
    '''
    return '''
        function on_load()
            deje.debug('on_load')
        end

        function on_resource_update()
            deje.debug('on_resource_update')
        end

        function on_scratch_update()
            deje.debug('on_scratch_update')
        end
    '''

def test_bootstrap(content):
    from deje import document, resource
    doc = document.Document()
    handler = resource.Resource('/handler.lua', content, 'The primary handler', 'text/lua')
    doc.add_resource(handler)
    return doc
