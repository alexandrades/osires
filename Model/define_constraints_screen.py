from Model.base_model import BaseScreenModel


class DefineConstraintsScreenModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.define_constraints_screen.DefineConstraintsScreen.DefineConstraintsScreenView` class.
    """

    def __init__(self) -> None:
        super().__init__()
        self._output_list = []
        self._constraint_list = []

    @property
    def output_list(self):
        return self._output_list
    
    @output_list.setter
    def output_list(self, variables):
        self._output_list = variables
        self.notify_observers('define constraints screen')

    @property
    def constraint_list(self):
        return self._constraint_list
    
    @constraint_list.setter
    def constraint_list(self, constraints):
        self._constraint_list = constraints
        self.notify_observers('define constraints screen')