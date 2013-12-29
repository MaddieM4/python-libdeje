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
    doc.add_resource(handler_resource(handler_name), False)
    doc.freeze()
    return doc

# Prebaked handlers for Lua interpreter

def echo_chamber():
    '''
    Diagnostic, prints stuff on events.
    '''
    return '''
        function on_resource_update(path, propname, oldpath)
            deje.debug('on_resource_update ' .. path .. " " .. propname)
            if propname == 'path' then
                deje.debug(oldpath .. " was moved to " .. path)
            end
        end

        function trigger_event(value)
            deje.event(value)
        end

        function event_test(ev, author)
            if ev == "example" then
                return true
            else
                return false
            end
        end

        function on_event_achieve(set_resource, ev, author)
            deje.debug("Event '" .. tostring(ev) .. "' achieved.")
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
    Every event requires approval from Mitzi and Atlas. Same for reads.
    '''
    return '''
        function event_test(ev, author)
            return true
        end

        function on_event_achieve(set_resource, ev, author)
            set_resource(ev.path, ev.property, ev.value)
        end

        function on_resource_update()
        end

        function quorum_participants()
            return { 
                "mitzi@lackadaisy.com",
                "atlas@lackadaisy.com"
            }
        end

        readers = { 
            "mitzi@lackadaisy.com",
            "atlas@lackadaisy.com",
            "victor@lackadaisy.com"
        }
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
    '''
    return '''
        function on_resource_update(path, propname, oldpath)
            return "pumpernickel"
        end

        function event_test(ev, author)
            return "perfidia"
        end

        function on_event_achieve(set_resource, ev, author)
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
