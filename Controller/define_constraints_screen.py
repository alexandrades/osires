import importlib

import View.DefineConstraintsScreen.define_constraints_screen
from Utility.temp_files_handler import TempFilesHandler

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
#importlib.reload(View.DefineConstraintsScreen.define_constraints_screen)




class DefineConstraintsScreenController:
    """
    The `DefineConstraintsScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.define_constraints_screen.DefineConstraintsScreenModel
        self.view = View.DefineConstraintsScreen.define_constraints_screen.DefineConstraintsScreenView(controller=self, model=self.model)

    def get_view(self) -> View.DefineConstraintsScreen.define_constraints_screen:
        return self.view
    
    def set_initial_values(self) -> None:
        self.model.constraint_list = self.view.app.repository.constraints
        self.model.output_list = TempFilesHandler.get_output_list(self.view.app.repository.model_file)
    
    def get_output_list(self):
        return self.model.output_list
    
    def update_repository(self):
        self.view.app.repository.constraints = self.model.constraint_list
    
    def previous_screen(self):
        self.update_repository()
        self.view.manager_screens.current = "define params screen"

    def next_screen(self):
        self.update_repository()
        self.view.manager_screens.current = "define method screen"
    
    def update(self):
        self.view.constraint_list = self.model.constraint_list
        self.view.output_list = self.model.output_list
