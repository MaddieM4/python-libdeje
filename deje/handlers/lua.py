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

from __future__ import print_function
from deje import document, resource

def handler_text(handler_name):
    functions = {
        "echo_chamber" : echo_chamber,
        "tag_team"     : tag_team,
        "psycho_ward"  : psycho_ward,
    }
    return functions[handler_name]()

def handler_resource(handler_name):
    return resource.Resource(
        '/handler.lua',
         handler_text(handler_name),
         handler_name,
         'text/lua'
    )

def handler_document(handler_name):
    doc = document.Document(handler_name)
    doc.add_resource(handler_resource(handler_name))
    return doc

# Prebaked handlers for Lua interpreter

def echo_chamber():
    '''
    Diagnostic, prints stuff on events.

    >>> from deje import testing
    >>> doc = testing.handler_lua(echo_chamber())

    Test on_resource_update

    >>> exampletxt = resource.Resource('/example.txt', 'blerg', type='text/plain')
    >>> doc.add_resource(exampletxt)
    on_resource_update /example.txt add
    >>> exampletxt.type = "text/html"
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
    >>> doc.animus.interpreter.call("trigger_checkpoint", "no dice") #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ValueError: Checkpoint ...'no dice' was not valid

    Test document properties

    >>> doc.get_participants() #doctest: +ELLIPSIS
    [...'anonymous']
    >>> doc.get_thresholds() == { 'read': 1, 'write': 1 }
    True

    Test request protocol mechanism

    >>> doc.get_request_protocols() #doctest: +ELLIPSIS
    [...'echo-chamber-1']
    >>> def pull_to_result(x):
    ...     print(x)
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

        function on_checkpoint_achieve(set_resource, cp, author)
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

        function on_checkpoint_achieve(set_resource, cp, author)
            set_resource(cp.path, cp.property, cp.value)
        end

        function on_resource_update()
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

def psycho_ward():
    '''
    Diagnostic, returns nonsense values.

    >>> from deje import testing
    >>> from deje.interpreters.lua import HandlerReturnError
    >>> doc = testing.handler_lua(psycho_ward())

    Normally, for this part, we'd just show tracebacks. But the printed output is
    different between Python 2 and 3, so we have to appease the doctest gods.

    >>> try:
    ...     doc.get_participants()
    ... except HandlerReturnError as e:
    ...     print(e) #doctest: +ELLIPSIS
    quorum_participants() returned 7, <... 'list'> expected
    >>> try:
    ...     doc.get_thresholds()
    ... except HandlerReturnError as e:
    ...     print(e) #doctest: +ELLIPSIS
    quorum_thresholds() returned ...'shoestring', <... 'dict'> expected

    >>> try:
    ...     doc.get_request_protocols()
    ... except HandlerReturnError as e:
    ...     print(e) #doctest: +ELLIPSIS
    request_protocols() returned 9, <... 'list'> expected
    >>> def pull_to_result(x):
    ...     print(x)
    >>> doc.request(
    ...     pull_to_result,
    ...     "hello-world",
    ... )

    >>> try:
    ...     doc.can_read("example")
    ... except HandlerReturnError as e:
    ...     print(e) #doctest: +ELLIPSIS
    can_read('example') returned <Lua table at ...>, <... 'bool'> expected
    >>> try:
    ...     doc.can_write("example")
    ... except HandlerReturnError as e:
    ...     print(e) #doctest: +ELLIPSIS
    can_write('example') returned ...'blue', <... 'bool'> expected

    Lobotomize can_write() into always returning true, to test checkpoint_test

    >>> doc.execute("function can_write()\\n    return true\\nend")
    >>> try:
    ...     doc.checkpoint("comet")
    ... except HandlerReturnError as e:
    ...     print(e) #doctest: +ELLIPSIS
    checkpoint_test('comet','anonymous') returned ...'perfidia', <... 'bool'> expected

    '''
    return '''
        function on_resource_update(path, propname, oldpath)
            return "pumpernickel"
        end

        function checkpoint_test(cp, author)
            return "perfidia"
        end

        function on_checkpoint_achieve(set_resource, cp, author)
            return nil
        end

        function quorum_participants()
            return 7
        end

        function quorum_thresholds()
            return "shoestring"
        end

        function can_read()
            return {}
        end

        function can_write()
            return "blue"
        end

        function request_protocols()
            return 9
        end

        function on_host_request(callback, params)
            return "Nurok turoth"
        end
    '''
