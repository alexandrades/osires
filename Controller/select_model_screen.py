import importlib

import View.SelectModelScreen.select_model_screen
from Utility.choosefile import choosefile
from Utility.temp_files_handler import TempFilesHandler

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.SelectModelScreen.select_model_screen)




class SelectModelScreenController:
    """
    The `SelectModelScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.select_model_screen.SelectModelScreenModel
        self.view = View.SelectModelScreen.select_model_screen.SelectModelScreenView(controller=self, model=self.model)

    def get_view(self) -> View.SelectModelScreen.select_model_screen:
        return self.view
    
    def set_initial_values(self, instance):
        self.model.model_file_path = self.view.app.repository.model_file_path
        self.model.input_file_path = self.view.app.repository.input_file_path
        self.model.output_file_path = self.view.app.repository.output_file_path

    
    def get_model_file_path(self):
        file_path = choosefile(filters=['*.cfg'])
        try:
            self.model.model_file_path = file_path[0]
            self.update_repository()
            # with open(self.selected_file, 'r') as config_file:
            #     self.simulation_config = json.load(config_file)

            # with open(f'config/{self.simulation_config["Model"][:-4]}.config', 'w') as json_config:
            #     json.dump(self.simulation_config, json_config, indent=4)
            # self.next_screen()
        except Exception as e:
            pass
    
    def get_input_file_path(self):
        file_path = choosefile(filters=['*.csv', '*.txt'])
        try:
            self.model.input_file_path = file_path[0]
            self.update_repository()
            # with open(self.selected_file, 'r') as config_file:
            #     self.simulation_config = json.load(config_file)

            # with open(f'config/{self.simulation_config["Model"][:-4]}.config', 'w') as json_config:
            #     json.dump(self.simulation_config, json_config, indent=4)
            # self.next_screen()
        except Exception as e:
            pass
    
    def get_output_file_path(self):
        file_path = choosefile(filters=['*.dat', '*.csv'])
        try:
            self.model.output_file_path = file_path[0]
            self.update_repository()
            # with open(self.selected_file, 'r') as config_file:
            #     self.simulation_config = json.load(config_file)

            # with open(f'config/{self.simulation_config["Model"][:-4]}.config', 'w') as json_config:
            #     json.dump(self.simulation_config, json_config, indent=4)
            # self.next_screen()
        except Exception as e:
            pass

    def update_repository(self):
        self.view.app.repository.model_file_path = self.model.model_file_path
        self.view.app.repository.input_file_path = self.model.input_file_path
        self.view.app.repository.output_file_path = self.model.output_file_path
    
    def previous_screen(self):
        self.view.manager_screens.current = 'main screen'
    
    def next_screen(self):
        TempFilesHandler.create_temp_files(self.model.model_file_path, self.model.input_file_path)
        self.view.manager_screens.current = 'define params screen'

    def update(self):
        self.view.model_file_path = self.model.model_file_path
        self.view.input_file_path = self.model.input_file_path
        self.view.output_file_path = self.model.output_file_path
        self.view.model_is_changed()
