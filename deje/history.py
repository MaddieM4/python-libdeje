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

class History(object):
    '''
    Represents a timeline of Events, with HistoryStates acting as "keyframes",
    to borrow a term from animation.
    '''
    def __init__(self, initial_state, events = []):
        self.states = {}
        self.events = []
        self.events_by_hash = {}

        self.add_state(initial_state)
        self.add_events(events)

    def add_state(self, state):
        self.states[state.hash] = state

    def add_event(self, event):
        self.events.append(event)
        self.events_by_hash[event.hash] = event

    def add_events(self, events):
        for event in events:
            self.add_event(event)

    @property
    def initial_state(self):
        if None in self.states:
            return self.states[None]
        else:
            for event in self.events:
                h = event.hash()
                if h in self.states:
                    return self.states[h]
            raise KeyError("No initial state found!")

    @property
    def orphan_states(self):
        return [h for h in self.states.keys() if not h in self.events_by_hash]

    @property
    def latest_existing_state(self):
        for event in self.events.reverse():
            h = event.hash()
            if h in self.states:
                return self.states[h]
        raise KeyError("No latest state found!")
