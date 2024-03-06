from Model.base_model import BaseScreenModel
from kivy.properties import StringProperty


class MainScreenModel(BaseScreenModel):
    def __init__(self) -> None:
        super().__init__()
        self._osires_file = ""

    @property
    def osires_file(self):
        return self._osires_file
    
    @osires_file.setter
    def osires_file(self, file):
        self._osires_file = file
        self.notify_observers('main screen')
        
    """
    Implements the logic of the
    :class:`~View.main_screen.MainScreen.MainScreenView` class.
    """

