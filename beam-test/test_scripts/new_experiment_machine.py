# TODO: Consider removing the state argument from actions and conditions.
#       States aren't a good place to store data because the method to
#       initialize variables there is a bit strange.
#       Probably better to just use "global" variables in the experiment's scope.

from typing import Callable
import logging

# -------------------------------------- #
# Classes
# -------------------------------------- #

class ExperimentState():
    """Represents an experiment state.
    
    Parameters:
        name (str): The name of this state. Must be unique to the experiment.
        actions (function): A function representing the actions to be done in this state.
            This function must accept two parameters:
                The parent experiment object.
                This state object.
            These allow access to experiment-level and state-level variables.
    """
    def __init__(self, name: str, actions: Callable) -> None:
        self.name = name
        self.__action_function = actions

    def do_actions(self, experiment) -> str:
        """Runs the state actions by calling the action function."""
        return self.__action_function(experiment)

class Experiment():
    def __init__(self, logging = None, single_step = False) -> None:
        # -------------------------------------- #
        # "Private" Member Variables
        # -------------------------------------- #
        
        # Ends execution of states when set to True.
        self.__stop = False

        # Store the states in a dictionary.
        # Format is "State Name": State Object
        self.__states = dict()

        # Stores the name of the next state to run.
        self.__next_state_name = ""

        # Logger for state transitions
        self._logging = logging

        self._single_step = single_step
        # -------------------------------------- #
    
    # -------------------------------------- #
    # "Private" Methods
    # -------------------------------------- #

    def __run_state(self, state_name: str):
        """Runs a specific state."""
        if self._single_step:
            input(f"Press enter to continue for state:{state_name}")
        self.__current_state = state_name
        if self._logging:
            self._logging.info("STATE:"+state_name)
        target_state = self.__states[state_name]
        result = target_state.do_actions(self)
        #print("result state="+result)
        return result

    # -------------------------------------- #
    # Public Methods
    # -------------------------------------- #

    def add_state(self, new_state: ExperimentState) -> None:
        """Register a new state with the experiment.
        
        Throws an error if a state with that name already exists.
        """
        # Throw error if state already exists.
        assert new_state.name not in self.__states.keys(), f"State '{new_state.name}' already exists."
        # Save the state in this experiment by it's name.
        self.__states[new_state.name] = new_state

    def get_current_state(self) -> str:
        """Returns the name of the current state that is running."""
        return self.__current_state

    def set_next_state(self, state_name: str) -> None:
        """This sets the next state that will be run.

        Parameters:
            state_name (str): The name of the next state to run.
        """
        # Throw an error if the target state doesn't exist in this experiment.
        assert state_name in self.__states.keys(), f"State '{state_name}' doesn't exist."
        # Save the name of the next state to execute.
        self.__next_state_name = state_name

    def start(self) -> None:
        """Starts/runs the experiment by executing the next state."""
        # Unset stop flag before starting.
        self.__stop = False
        # Run while stop flag is not set.
        while not self.__stop:
            #print("cur_state:"+self.__next_state_name)
            next_state_str = self.__run_state(self.__next_state_name)
            #print("next state="+next_state_str)
            self.set_next_state(next_state_str)

    def stop(self) -> None:
        """Stops the experiment at the end of the current state."""
        self.__stop = True


# -------------------------------------- #
# Usage Example
# -------------------------------------- #
if __name__ == "__main__":
    # Import module/script here.
    from time import sleep

    # Create a new experiment object.
    experiment = Experiment()

    # -------------------------------------- #
    # Creating states.
    # -------------------------------------- #

    # Define some state actions.
    def initial_actions(experiment):
        print("This is the initial state!")
        experiment.counter = 0
        return "Increment State"

    # Create the state object.
    initial_state = ExperimentState("Initial State",initial_actions)

    # Add state to experiment.
    experiment.add_state(initial_state)

    # -------------------------------------- #
    threshold = 5

    def increment_actions(experiment):
        experiment.counter += 1
        print(f"Incremented Counter: {experiment.counter - 1} -> {experiment.counter}")
        # print("Now sleeping for 1 second.")
        sleep(1)
        if experiment.counter >= threshold:
            return "End State"
        return "Increment State"

    experiment.add_state(ExperimentState("Increment State",increment_actions))

    # -------------------------------------- #

    def end_state_actions(ex):
        ex.stop()
        return "End State"
    experiment.add_state(ExperimentState("End State",end_state_actions,))

    # -------------------------------------- #
    # Running the experiment.
    # -------------------------------------- #

    # Set the first state and start the experiment.
    experiment.set_next_state("Initial State")
    experiment.start()
    print(f"Experiment finished in state: {experiment.get_current_state()}")