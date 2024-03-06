from Model.base_model import BaseScreenModel


class SelectModelScreenModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.select_model_screen.SelectModelScreen.SelectModelScreenView` class.
    """

    def __init__(self) -> None:
        super().__init__()
        self._model_file_path = ""
        self._input_file_path = ""
        self._output_file_path = ""

    @property
    def model_file_path(self):
        return self._model_file_path
    
    @model_file_path.setter
    def model_file_path(self, model_file_path):
        self._model_file_path = model_file_path
        self.notify_observers('select model screen')
    
    @property
    def input_file_path(self):
        return self._input_file_path
    
    @input_file_path.setter
    def input_file_path(self, input_file_path):
        self._input_file_path = input_file_path
        self.notify_observers('select model screen')
    
    @property
    def output_file_path(self):
        return self._output_file_path
    
    @output_file_path.setter
    def output_file_path(self, output_file_path):
        self._output_file_path = output_file_path
        self.notify_observers('select model screen')