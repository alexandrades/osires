# The screen's dictionary contains the objects of the models and controllers
# of the screens of the application.

from Model.main_screen import MainScreenModel
from Controller.main_screen import MainScreenController
from Model.select_screen import SelectScreenModel
from Controller.select_screen import SelectScreenController
from Model.select_model_screen import SelectModelScreenModel
from Controller.select_model_screen import SelectModelScreenController
from Model.define_params_screen import DefineParamsScreenModel
from Controller.define_params_screen import DefineParamsScreenController
from Model.method_selection_screen import MethodSelectionScreenModel
from Controller.method_selection_screen import MethodSelectionScreenController
from Model.define_constraints_screen import DefineConstraintsScreenModel
from Controller.define_constraints_screen import DefineConstraintsScreenController
from Model.define_method_screen import DefineMethodScreenModel
from Controller.define_method_screen import DefineMethodScreenController
from Model.main_screen import MainScreenModel
from Controller.main_screen import MainScreenController
from Model.select_screen import SelectScreenModel
from Controller.select_screen import SelectScreenController
from Model.select_model_screen import SelectModelScreenModel
from Controller.select_model_screen import SelectModelScreenController
from Model.define_params_screen import DefineParamsScreenModel
from Controller.define_params_screen import DefineParamsScreenController
from Model.method_selection_screen import MethodSelectionScreenModel
from Controller.method_selection_screen import MethodSelectionScreenController
from Model.define_constraints_screen import DefineConstraintsScreenModel
from Controller.define_constraints_screen import DefineConstraintsScreenController
from Model.opt_result_screen import OptResultScreenModel
from Controller.opt_result_screen import OptResultScreenController

screens = {
    'main screen': {
        'model': MainScreenModel,
        'controller': MainScreenController,
    },
    'select model screen': {
        'model': SelectModelScreenModel,
        'controller': SelectModelScreenController,
    },
    'define params screen': {
        'model': DefineParamsScreenModel,
        'controller': DefineParamsScreenController,
    },
    'method selection screen': {
        'model': MethodSelectionScreenModel,
        'controller': MethodSelectionScreenController,
    },
    'define constraints screen': {
        'model': DefineConstraintsScreenModel,
        'controller': DefineConstraintsScreenController
    },
    'define method screen': {
        'model': DefineMethodScreenModel,
        'controller': DefineMethodScreenController
    },
    'opt result screen': {
        'model': OptResultScreenModel,
        'controller': OptResultScreenController
    }
}