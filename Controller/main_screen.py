import importlib
import os
import json

from Utility.choosefile import choosefile


import View.MainScreen.main_screen

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.MainScreen.main_screen)




class MainScreenController:
    """
    The `MainScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = View.MainScreen.main_screen.MainScreenView(controller=self, model=self.model)

    def get_view(self) -> View.MainScreen.main_screen:
        return self.view
    
    def creste_new_optimization(self):
        self.view.manager_screens.current = 'select model screen'

    def get_osires_file_path(self):
        file_path = choosefile(filters=["*.osires"])
        try:
            self.model.osires_file = file_path[0]
            # with open(self.selected_file, 'r') as config_file:
            #     self.simulation_config = json.load(config_file)

            # with open(f'config/{self.simulation_config["Model"][:-4]}.config', 'w') as json_config:
            #     json.dump(self.simulation_config, json_config, indent=4)
            # self.next_screen()

            self.update_repository()
        except Exception as e:
            pass

        self.creste_new_optimization()

        # self.update_opt_config()

    def update_repository(self):
        with open(self.model.osires_file, 'r') as f_osires_file:
            osires_file = json.load(f_osires_file)
        self.view.app.repository.osires_file = self.model.osires_file
        self.view.app.repository.model_file_path = osires_file['ModelPath']
        self.view.app.repository.input_file_path = osires_file['InputPath']
        self.view.app.repository.output_file_path = osires_file['OutputPath']
        self.view.app.repository.resources = osires_file['Resources']
        self.view.app.repository.constraints = osires_file['Constraints']
        self.view.app.repository.best_values = osires_file['Best']
        self.view.app.repository.opt_method = osires_file['OptMethod']
        self.view.app.repository.opt_type = osires_file['OptType']
        self.view.app.repository.ml_algorithm = osires_file['MlAlgorithm']
        self.view.app.repository.min_simulations_train = osires_file['MinSimulationsTrain']


    def update(self):
        self.view.osires_file = self.model.osires_file
