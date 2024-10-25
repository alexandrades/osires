from Utility.choosefile import choosefile
from Utility.modules_utils import save_simulation
import importlib
import os
import json

import View.DefineMethodScreen.define_method_screen

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
#importlib.reload(View.DefineMethodScreen.define_method_screen)




class DefineMethodScreenController:
    """
    The `DefineMethodScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.define_method_screen.DefineMethodScreenModel
        self.view = View.DefineMethodScreen.define_method_screen.DefineMethodScreenView(controller=self, model=self.model)

    def get_view(self) -> View.DefineMethodScreen.define_method_screen:
        return self.view
    
    def set_initial_values(self) -> None:
        self.model.opt_type = self.view.app.repository.opt_type
        self.model.opt_method = self.view.app.repository.opt_method
        self.model.ml_algorithm = self.view.app.repository.ml_algorithm
        self.model.min_simulations_train = self.view.app.repository.min_simulations_train

    def update_repository(self):
        self.view.app.repository.opt_type = self.model.opt_type
        self.view.app.repository.opt_method = self.model.opt_method
        self.view.app.repository.ml_algorithm = self.model.ml_algorithm
        self.view.app.repository.min_simulations_train = self.model.min_simulations_train
        self.view.app.repository.osires_file = self.model.save_path

    def previous_screen(self):
        self.update_repository()
        self.view.manager_screens.current = "define constraints screen"

    def run_opt(self):
        self.update_repository()
        self.view.manager_screens.current = "opt result screen"

    def save_opt_options(self):
        cwd = os.getcwd()
        file_path = choosefile(filters=['*.osires'])
        self.model.save_path = file_path[0]
        save_simulation(self.model.save_path, self.view.app.repository.get_dict_config())

        os.chdir(cwd)

    def update(self):
        self.update_repository()
        self.view.opt_method = self.model.opt_method
        self.view.opt_type = self.model.opt_type
        self.view.ml_algorithm = self.model.ml_algorithm
        self.view.min_simulations_train = str(self.model.min_simulations_train)
        self.view.save_path = self.model.save_path
