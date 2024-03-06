from Model.base_model import BaseScreenModel


class DefineParamsScreenModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.define_params_screen.DefineParamsScreen.DefineParamsScreenView` class.
    """

    def __init__(self) -> None:
        super().__init__()
        self._resources_names = []
        self._resources_list = {}

    @property
    def resources_names(self):
        return self._resources_names
    
    @resources_names.setter
    def resources_names(self, names):
        self._resources_names = names
        self.notify_observers('define params screen')

    @property
    def resources_list(self):
        return self._resources_list
    
    @resources_list.setter
    def resources_list(self, resources):
        self._resources_list = resources
        self.notify_observers('define params screen')