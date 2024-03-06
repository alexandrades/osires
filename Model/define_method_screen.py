from Model.base_model import BaseScreenModel


class DefineMethodScreenModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.define_method_screen.DefineMethodScreen.DefineMethodScreenView` class.
    """

    def __init__(self) -> None:
        super().__init__()
        self._opt_method = ""
        self._opt_type = ""
        self._ml_algorithm = ""
        self._min_simulations_train = ""
        self._save_path = ""

    @property
    def opt_method(self):
        return self._opt_method
    
    @opt_method.setter
    def opt_method(self, opt_method):
        self._opt_method = opt_method
        self.notify_observers('define method screen')
        
    @property
    def opt_type(self):
        return self._opt_type
    
    @opt_type.setter
    def opt_type(self, opt_type):
        self._opt_type = opt_type
        self.notify_observers('define method screen')
        
    @property
    def ml_algorithm(self):
        return self._ml_algorithm
    
    @ml_algorithm.setter
    def ml_algorithm(self, ml_algorithm):
        self._ml_algorithm = ml_algorithm
        self.notify_observers('define method screen')

    @property
    def min_simulations_train(self):
        return self._min_simulations_train
    
    @min_simulations_train.setter
    def min_simulations_train(self, min_simulations_train):
        self._min_simulations_train = min_simulations_train
        self.notify_observers('define method screen')

    @property
    def save_path(self):
        return self._save_path
    
    @save_path.setter
    def save_path(self, save_path):
        self._save_path = save_path
        print("Moddel: ", self._save_path)
        self.notify_observers('define method screen')