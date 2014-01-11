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
        '/handler',
         handler_text(handler_name),
         handler_name,
         'direct/json'
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
    return {
        'on_resource_update' : '''
            deje.debug('on_resource_update ' .. path .. " " .. propname)
            if propname == 'path' then
                deje.debug(oldpath .. " was moved to " .. path)
            end
        ''',

        'trigger_event' : '''
            deje.event(value)
        ''',

        'event_test' : '''
            if ev == "example" then
                return true
            else
                return false
            end
        ''',

        'on_event_achieve' : '''
            deje.debug("Event '" .. tostring(ev) .. "' achieved.")
        ''',

        'quorum_participants' : '''
            return { deje.get_ident() }
        ''',

        'quorum_thresholds' : '''
            return {read=1, write=1}
        ''',

        'can_read' : '''
            return true
        ''',

        'can_write' : '''
            return true
        ''',

        'request_protocols' : '''
            return { "echo-chamber-1" }
        ''',

        'on_host_request' : '''
            local rtype = params[0]
            if rtype == "hello-world" then
                callback("Request protocol mechanism says hello.")
            end
        ''',
    }

def tag_team():
    '''
    Every event requires approval from Mitzi and Atlas. Same for reads.
    '''
    return {
        'event_test': '''
            return true
        ''',

        'on_event_achieve': '''
            set_resource(ev.path, ev.property, ev.value)
        ''',

        'quorum_participants': '''
            return { 
                "mitzi@lackadaisy.com",
                "atlas@lackadaisy.com"
            }
        ''',

        'readers' : [
            "mitzi@lackadaisy.com",
            "atlas@lackadaisy.com",
            "victor@lackadaisy.com",
        ],
        'writers' : [
            "mitzi@lackadaisy.com",
            "atlas@lackadaisy.com",
        ],

        'can_read': '''
            raw = deje.get_resource('/handler').content.readers
            readers = deje.clone_table(raw, {})

            for i, v in pairs(readers) do
                if v == name then
                    return true
                end
            end
            return false
        ''',

        'can_write': '''
            raw = deje.get_resource('/handler').content.writers
            writers = deje.clone_table(raw, {})

            for i, v in pairs(writers) do
                if v == name then
                    return true
                end
            end
            return false
        ''',

        'quorum_thresholds': '''
            return {read=2, write=2}
        ''',
    }

def psycho_ward():
    '''
    Diagnostic, returns nonsense values.
    '''
    return {
        'on_resource_update': '''
            return "pumpernickel"
        ''',

        'event_test': '''
            return "perfidia"
        ''',

        'on_event_achieve': '''
            return nil
        ''',

        'quorum_participants': '''
            return 7
        ''',

        'quorum_thresholds': '''
            return "shoestring"
        ''',

        'can_read': '''
            return {}
        ''',

        'can_write': '''
            return "blue"
        ''',

        'request_protocols': '''
            return 9
        ''',

        'on_host_request': '''
            return "Nurok turoth"
        ''',
    }
