from Model.base_model import BaseScreenModel
import sys

from typing import List

class OsiresFileHandler(BaseScreenModel):
    def __init__(self) -> None:
        super().__init__()
        self._osires_file = ""
        self._model_file = "CorteEDobra3.cfg"
        self._model_file_path = "C:\\Users\\alexa\\OneDrive\\Área de Trabalho\\CorteEDobra3.cfg"
        self._input_file = "inputs.csv"
        self._input_file_path = "C:\\Users\\alexa\\OneDrive\\Área de Trabalho\\inputs.csv"
        self._output_file = "CorteEDobra3.dat"
        self._output_file_path = "C:\\Users\\alexa\\OneDrive\\Área de Trabalho\\CorteEDobra3.dat"
        self._resources = {'OperatorsCut1': {'minimum_value': 1, 'maximum_value': 20, 'step_value': 1, 'initial_value': 1}, 'OperatorsCut2': {'minimum_value': 1, 'maximum_value': 20, 'step_value': 1, 'initial_value': 1}, 'OperatorsFold1': {'minimum_value': 1, 'maximum_value': 20, 'step_value': 1, 'initial_value': 1}, 'OperatorsFold2': {'minimum_value': 1, 'maximum_value': 20, 'step_value': 1, 'initial_value': 1}}
        self._constraints = []
        self._best_values = {'Params': [], 'Value': '0'}
        self._opt_type = ""
        self._opt_method = ""
        self._ml_algorithm = ""
        self._min_simulations_train = ""

    @property
    def osires_file(self) -> str:
        return self._osires_file

    @osires_file.setter
    def osires_file(self, value: str) -> None:
        self._osires_file = value

    @property
    def model_file(self) -> str:
        return self._model_file

    @model_file.setter
    def model_file(self, value: str) -> None:
        self._model_file = value

    @property
    def model_file_path(self) -> str:
        return self._model_file_path

    @model_file_path.setter
    def model_file_path(self, value: str) -> None:
        self._model_file_path = value
        print("Value: ", value)
        self.model_file = value.split('\\')[-1]

    @property
    def input_file(self) -> str:
        return self._input_file

    @input_file.setter
    def input_file(self, value: str) -> None:
        self._input_file = value

    @property
    def input_file_path(self) -> str:
        return self._input_file_path

    @input_file_path.setter
    def input_file_path(self, value: str) -> None:
        self._input_file_path = value
        self._input_file = value.split('\\')[-1]

    @property
    def output_file(self) -> str:
        return self._output_file

    @output_file.setter
    def output_file(self, value: str) -> None:
        self._output_file = value

    @property
    def output_file_path(self) -> str:
        return self._output_file_path

    @output_file_path.setter
    def output_file_path(self, value: str) -> None:
        self._output_file_path = value
        self._output_file = value.split('\\')[-1]

    @property
    def resources(self) -> dict:
        return self._resources

    @resources.setter
    def resources(self, value: dict) -> None:
        self._resources = value

    @property
    def constraints(self) -> List:
        return self._constraints

    @constraints.setter
    def constraints(self, value: List) -> None:
        self._constraints = value

    @property
    def best_values(self) -> dict:
        return self._best_values

    @best_values.setter
    def best_values(self, value: dict) -> None:
        self._best_values = value

    @property
    def opt_method(self):
        return self._opt_method
    
    @opt_method.setter
    def opt_method(self, opt_method):
        self._opt_method = opt_method
        
    @property
    def opt_type(self):
        return self._opt_type
    
    @opt_type.setter
    def opt_type(self, opt_type):
        self._opt_type = opt_type
        
    @property
    def ml_algorithm(self):
        return self._ml_algorithm
    
    @ml_algorithm.setter
    def ml_algorithm(self, ml_algorithm):
        self._ml_algorithm = ml_algorithm

    @property
    def min_simulations_train(self):
        return self._min_simulations_train
    
    @min_simulations_train.setter
    def min_simulations_train(self, min_simulations_train):
        self._min_simulations_train = min_simulations_train

    def get_dict_config(self):
        return {
            "Model": self.model_file,
            "ModelPath": self.model_file_path,
            "Input": self.input_file,
            "InputPath": self.input_file_path,
            "Output": self.output_file,
            "OutputPath": self.output_file_path,
            "Resources": self.resources,
            "Constraints": self.constraints,
            "Best": self.best_values,
            "OptMethod": self.opt_method,
            "OptType": self.opt_type,
            "MlAlgorithm": self.ml_algorithm,
            "MinSimulationsTrain": self.min_simulations_train
        }