import importlib

import View.DefineParamsScreen.define_params_screen
from Utility.temp_files_handler import TempFilesHandler

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
#importlib.reload(View.DefineParamsScreen.define_params_screen)




class DefineParamsScreenController:
    """
    The `DefineParamsScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.define_params_screen.DefineParamsScreenModel
        self.view = View.DefineParamsScreen.define_params_screen.DefineParamsScreenView(controller=self, model=self.model)

    def get_view(self) -> View.DefineParamsScreen.define_params_screen:
        return self.view
    
    def set_initial_values(self) -> None:
        self.model.resources_list = self.view.app.repository.resources
    
    def get_resources_names(self):
        self.model.resources_names = TempFilesHandler.get_resources_names(self.view.app.repository.input_file)
        return self.model.resources_names
    
    def update_params(self, instance, value, resource, param):
        self.model.resources_list[resource][param] = value
    
    def update_repository(self):
        self.model.resources_list = self.view.resource_list
        self.view.app.repository.resources = self.model.resources_list
    
    def previous_screen(self):
        self.update_repository()
        self.view.manager_screens.current = 'select model screen'

    def next_screen(self):
        print(self.view.resource_list)
        self.update_repository()
        self.view.manager_screens.current = 'define constraints screen'

    def update(self):
        self.view.resource_list = self.model.resources_list
        self.view.resources_names = self.model.resources_names
        self.view.model_is_changed()
