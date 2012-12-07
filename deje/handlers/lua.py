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

    >>> from deje import testing
    >>> doc = testing.handler_lua(echo_chamber())

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
    Checkpoint 'example' achieved.
    >>> doc.animus.interpreter.call("trigger_checkpoint", "no dice")
    Traceback (most recent call last):
    ValueError: Checkpoint u'no dice' was not valid

    Test document properties

    >>> doc.get_participants()
    [u'anonymous']
    >>> doc.get_thresholds() == { 'read': 1, 'write': 1 }
    True

    Test request protocol mechanism

    >>> doc.get_request_protocols()
    [u'echo-chamber-1']
    >>> def pull_to_result(x):
    ...     print x
    >>> doc.request(
    ...     pull_to_result,
    ...     "hello-world",
    ... )
    Request protocol mechanism says hello.

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

        function checkpoint_test(cp, author)
            if cp == "example" then
                return true
            else
                return false
            end
        end

        function on_checkpoint_achieve(cp, author)
            deje.debug("Checkpoint '" .. tostring(cp) .. "' achieved.")
        end

        function quorum_participants()
            return { deje.get_ident() }
        end

        function quorum_thresholds()
            return {read=1, write=1}
        end

        function can_read()
            return true
        end

        function can_write()
            return true
        end

        function request_protocols()
            return { "echo-chamber-1" }
        end

        function on_host_request(callback, params)
            local rtype = params[0]
            if rtype == "hello-world" then
                callback("Request protocol mechanism says hello.")
            end
        end
    '''

def tag_team():
    '''
    Every checkpoint requires approval from Mitzi and Atlas. Same for reads.
    '''
    return '''
        function checkpoint_test(cp, author)
            return true
        end

        function on_checkpoint_achieve(cp, author)
            -- deje.debug("Checkpoint '" .. tostring(cp) .. "' achieved.")
        end

        function quorum_participants()
            return { 'mitzi@lackadaisy.com', 'atlas@lackadaisy.com' }
        end

        readers = { 'mitzi@lackadaisy.com', 'atlas@lackadaisy.com', 'victor@lackadaisy.com' }
        writers = quorum_participants()

        function can_read(name)
            for i, v in pairs(readers) do
                if v == name then
                    return true
                end
            end
            return false
        end

        function can_write(name)
            for i, v in pairs(writers) do
                if v == name then
                    return true
                end
            end
            return false
        end

        function quorum_thresholds()
            return {read=2, write=2}
        end
    '''
