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

from deje.tests.stream     import StreamTest

from ejtp.identity.core    import Identity
from deje.owner            import Owner
from deje.resource         import Resource
from deje.handlers         import handler_document
from deje.interpreters.lua import HandlerReturnError

class TestLuaHandler(StreamTest):
    def setUp(self):
        StreamTest.setUp(self)

        self.doc = handler_document(self.name)
        self.identity = Identity(
            "jtkirk@starfleet.gov",
            ['rotate',5],
            ['local', None, "kirk"]
        )
        self.owner = Owner(self.identity, make_jack = False)
        self.owner.own_document(self.doc)

class TestLuaHandlerEchoChamber(TestLuaHandler):
    @property
    def name(self):
        return "echo_chamber"

    def test_on_resource_update(self):
        exampletxt = Resource(
            '/example.txt',
            'blerg',
            type='text/plain'
        )
        self.doc.add_resource(exampletxt)
        self.assertOutput("on_resource_update /example.txt add\n")

        exampletxt.type = "text/html"
        self.assertOutput("on_resource_update /example.txt type\n")
        exampletxt.content = "I like turtles."
        self.assertOutput("on_resource_update /example.txt content\n")
        exampletxt.comment = "Meaningless drivel"
        self.assertOutput("on_resource_update /example.txt comment\n")
        exampletxt.path = "/fridge/turtles.txt"
        self.assertOutput(
            "on_resource_update /fridge/turtles.txt path\n" +
            "/example.txt was moved to /fridge/turtles.txt\n"
        )

    def test_event(self):
        self.doc.interpreter.call("trigger_event", "example")
        self.assertOutput("Event 'example' achieved.\n")

        self.assertRaises(
            ValueError,
            self.doc.interpreter.call,
            "trigger_event", "no dice"
        )

    def test_document_properties(self):
        self.assertEquals(
            self.doc.get_participants(), 
            [self.identity]
        )
        self.assertEquals(
            self.doc.get_thresholds(),
            {'read': 1, 'write': 1}
        )

    def test_request_protocol(self):
        self.assertEquals(
            self.doc.get_request_protocols(),
            ['echo-chamber-1']
        )

        results = []
        def pull_to_result(x):
            results.append(x)

        self.doc.request(pull_to_result, "hello-world")
        self.assertEquals(
            results.pop(),
            "Request protocol mechanism says hello."
        )

class TestLuaHandlerPsychoWard(TestLuaHandler):
    @property
    def name(self):
        return "psycho_ward"

    def test_document_properties(self):
        properties = [
            (self.doc.get_participants,),
            (self.doc.get_thresholds,),
            (self.doc.get_request_protocols,),
            #(self.doc.can_read,  "example"),
            #(self.doc.can_write, "example"),
        ]
        for prop in properties:
            self.assertRaises(
                HandlerReturnError,
                *prop
            )

    def test_request_protocol(self):
        results = []
        def pull_to_result(x):
            results.append(x)

        self.doc.request(pull_to_result, "hello-world")
        self.assertEquals(
            results,
            []
        )

    def test_event(self):
        # Lobotomize can_write() into always returning true
        self.doc.execute("""
            function can_write()
                return true
            end
        """)

        self.assertRaises(
            HandlerReturnError,
            self.doc.event,
            "comet"
        )
