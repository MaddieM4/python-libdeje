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

from deje import document, resource

def echo_chamber():
    '''
    Diagnostic, prints stuff on events.

    >>> doc = test_bootstrap(echo_chamber())

    Test on_resource_update

    >>> exampletxt = resource.Resource('/example.txt', 'blerg', type='text/plain')
    >>> doc.add_resource(exampletxt)
    on_resource_update /example.txt add
    >>> exampletxt.type = "marshmallow/cloud"
    on_resource_update /example.txt type
    >>> exampletxt.content = "I like turtles."
    on_resource_update /example.txt content
    >>> exampletxt.comment = "Meaningless drivel"
    on_resource_update /example.txt comment
    >>> exampletxt.path = "/fridge/turtles.txt"
    on_resource_update /fridge/turtles.txt path
    /example.txt was moved to /fridge/turtles.txt

    Test checkpointing

    >>> doc.animus.interpreter.call("trigger_checkpoint", "example")
    Tested checkpoint u'example' and got result True
    Checkpoint 'example' achieved.
    >>> doc.animus.interpreter.call("trigger_checkpoint", "no dice")
    Tested checkpoint u'no dice' and got result False

    Test document properties

    >>> doc.get_participants()
    [u'anonymous']
    >>> doc.get_thresholds() == { 'read': 1, 'write': 1 }
    True
    '''
    '''

    Test request protocol mechanism

    >>> doc.get_request_protocols
    ["echo-chamber-1"]
    >>> result = None
    >>> def pull_to_result(x):
    ...     result = x
    >>> doc.request(
    ...     pull_to_result,
    ...     "hello-world",
    ... )
    >>> result
    "Request protocol mechanism says hello."

    '''
    return '''
        function on_resource_update(path, propname, oldpath)
            deje.debug('on_resource_update ' .. path .. " " .. propname)
            if propname == 'path' then
                deje.debug(oldpath .. " was moved to " .. path)
            end
        end

        function trigger_checkpoint(value)
            deje.checkpoint(value)
        end

        function checkpoint_test(cp)
            if cp == "example" then
                return true
            else
                return false
            end
        end

        function on_checkpoint_achieve(cp)
            deje.debug("Checkpoint '" .. tostring(cp) .. "' achieved.")
        end

        function quorum_participants()
            return { deje.get_ident() }
        end

        function quorum_thresholds()
            return {read=1, write=1}
        end
    '''

def test_bootstrap(content):
    doc = document.Document()
    handler = resource.Resource('/handler.lua', content, 'The primary handler', 'text/lua')
    doc.add_resource(handler)
    return doc
