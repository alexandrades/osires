from Model.base_model import BaseScreenModel


class OptResultScreenModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.opt_result_screen.OptResultScreen.OptResultScreenView` class.
    """

    def __init__(self) -> None:
        super().__init__()
        self._best_values = {}
        self._best_values_set = {}
        self._graph = {}

    @property
    def best_values(self):
        return self._best_values
    
    @best_values.setter
    def best_values(self, best_values):
        self._best_values = best_values
        print("Notify\n\n\n\n")
        self.notify_observers('opt result screen')
    
    @property
    def best_values_set(self):
        return self._best_values_set
    
    @best_values_set.setter
    def best_values_set(self, best_values_set):
        self._best_values_set = best_values_set
        self.notify_observers('opt result screen')

    @property
    def graph(self):
        return self._graph
    
    @graph.setter
    def graph(self, graph):
        self._graph = graph
