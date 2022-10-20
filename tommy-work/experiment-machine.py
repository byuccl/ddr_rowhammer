# -------------------------------------- #
# Classes Drafting
# -------------------------------------- #

# TODO: Consider removing the state argument from actions and conditions.
#       States aren't a good place to store data because the method to
#       initialize variables there is a bit strange.
#       Probably better to just use "global" variables in the experiment's scope.

from typing import Callable


class Transition():
    """Explicity stores a state transition.
    
    Parameters:
        condition (function): A function taking two objects as parameters (NewExperiment, ExperimentState) and returning a Boolean.
            This function will be called with the parent experiment and state objects do determine if the experiment should
            transition to the associated state. Experiment and state objects are passed so that member variables can be
            tested. Ideally, this function can be declared as a lambda in the initializer, but an existing function can
            be passed instead if Mealy outputs are desired.
        state_name (str): The name of the state to transition to if the condition is satisfied.
    """
    def __init__(self, condition: Callable, state_name: str) -> None:
        self.__test_condition = condition
        self.target_state = state_name

    def satisfied(self, experiment, state) -> bool:
        return self.__test_condition(experiment, state) == True

class ExperimentState():
    """Represents an experiment state.
    
    Parameters:
        name (str): The name of this state. Must be unique to the experiment.
        actions (function): A function representing the actions to be done in this state.
            This function must accept two parameters:
                The parent experiment object.
                This state object.
            These allow access to experiment-level and state-level variables.
        transitions (Transition): Some number of transition objects must follow the actions.
            Transitions will be checked in the order provided.
            The first transition satisfied (returning True) will be used.
            Subsequent transitions will not be checked if a prior transition is satisfied.
    """
    def __init__(self, name: str, actions: Callable, *args) -> None:
        self.name = name
        self.__action_function = actions
        self.__transition_table = args
        assert len(self.__transition_table) > 0, "No transitions were specified."

    def do_transitions(self, experiment) -> None:
        """Sets the experiment's next state based on provided transitions.
        
        If none are matched, error will be thrown."""
        # Check transition objects in order.
        for transition in self.__transition_table:
            # Check if conditions are satisfied.
            if transition.satisfied(experiment, self):
                # Set next state to transition target.
                experiment.set_next_state(transition.target_state)
                # Stop checking other conditions.
                return
        
        # Throw an error if no transition conditions were matched.
        assert False, f"No transition conditions were matched for state {self.name}."

    def do_actions(self, experiment) -> None:
        """Runs the state actions by calling the action function."""
        self.__action_function(experiment, self)

class Experiment():
    def __init__(self) -> None:
        # -------------------------------------- #
        # "Private" Member Variables
        # -------------------------------------- #
        
        # Ends execution of states when set to True.
        self.__stop = False

        # Store the states in a dictionary.
        # Format is "State Name": State Object
        self.__states = dict()

        # Stores the name of the next state to run.
        self.__next_state = ""
        # -------------------------------------- #
    
    # -------------------------------------- #
    # "Private" Methods
    # -------------------------------------- #

    def __run_state(self, state_name: str):
        """Runs a specific state."""
        self.__current_state = state_name
        target_state = self.__states[state_name]
        target_state.do_actions(self)
        target_state.do_transitions(self)

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

    def get_next_state(self) -> str:
        """Returns the name of the next state that will be run."""
        return self.__next_state

    def set_next_state(self, state_name: str) -> None:
        """This sets the next state that will be run.

        Parameters:
            state_name (str): The name of the next state to run.
        """
        # Throw an error if the target state doesn't exist in this experiment.
        assert state_name in self.__states.keys(), f"State '{state_name}' doesn't exist."
        # Save the name of the next state to execute.
        self.__next_state = state_name

    def start(self) -> None:
        """Starts/runs the experiment by executing the next state."""
        # Unset stop flag before starting.
        self.__stop = False
        # Run while stop flag is not set.
        while not self.__stop:
            self.__run_state(self.__next_state)
    
    def stop(self) -> None:
        """Stops the experiment at the end of the current state."""
        self.__stop = True

# -------------------------------------- #
# -------------------------------------- #
# Usage Drafting
# -------------------------------------- #
# -------------------------------------- #
from time import sleep

# Create a new experiment object.
experiment = Experiment()

# -------------------------------------- #
# Creating states.
# -------------------------------------- #

# Define some state actions.
def initial_actions(experiment, state):
    print("This is the initial state!")
    experiment.counter = 0

# Create the state object.
initial_state = ExperimentState(
    "Initial State",
    initial_actions,
    Transition(lambda ex, st: True, "Increment State")
)

# Add state to experiment.
experiment.add_state(initial_state)

# -------------------------------------- #
threshold = 5

def increment_actions(experiment, state):
    experiment.counter += 1
    print(f"Incremented Counter: {experiment.counter - 1} -> {experiment.counter}")
    # print("Now sleeping for 1 second.")
    sleep(1)

experiment.add_state(ExperimentState(
    "Increment State",
    increment_actions,
    Transition(lambda ex, st: ex.counter >= threshold, "End State"),
    # Transition(lambda ex, st: True, "Increment State")
))

# -------------------------------------- #

experiment.add_state(ExperimentState(
    "End State",
    lambda ex, st: ex.stop(),
    Transition(lambda ex, st: True, "End State")
))

# -------------------------------------- #
# Running the experiment.
# -------------------------------------- #

# Set the first state and start the experiment.
experiment.set_next_state("Initial State")
experiment.start()
print(f"Experiment finished in state: {experiment.get_current_state()}")