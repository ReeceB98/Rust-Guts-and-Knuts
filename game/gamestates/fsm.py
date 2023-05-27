import pyasge


class FSM:
    def __init__(self):
        """ Sets the state to None """
        self.current_state = None

    def setstate(self, state):
        """ Updates the function to call when updated """
        self.current_state = state

    def update(self, game_time: pyasge.GameTime):
        """ Calls the function assigned to current_state """
        if self.current_state is not None:
            self.current_state(game_time)