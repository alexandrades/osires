import importlib
import threading
import View.OptResultScreen.opt_result_screen

from Modules.Grasp import Grasp
from Modules.Scatter import Scatter
from Modules.ScatterAI import ScatterAI
from Modules.GraspAI import GraspAI
from Modules.PSO import PSO
from Modules.Firefly import FSO
from Utility.graph_generator import build_graph
import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'  # Oculta logs do Kivy
import kivy
kivy.logger.Logger.setLevel('WARNING')  # Ou 'ERROR' para exibir apenas erros
# from Modules.Scatter import Scatter, ScatterAI

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
#importlib.reload(View.OptResultScreen.opt_result_screen)




class OptResultScreenController:
    """
    The `OptResultScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.opt_result_screen.OptResultScreenModel
        self.view = View.OptResultScreen.opt_result_screen.OptResultScreenView(controller=self, model=self.model)

    def get_view(self) -> View.OptResultScreen.opt_result_screen:
        return self.view
    
    def set_initial_values(self) -> None:
        print("SET INITIAL VALUES \n\n")
        self.model.best_values = self.view.app.repository.best_values
        self.model.best_values_set = self.view.app.repository.best_values_set
        self.model.graph = build_graph(self.view.app.repository)

    def init_optimization(self):
        opt_method = self.view.app.repository.opt_method
        if opt_method == "Scatter":
            scatter = Scatter(self.view.app.repository, self.model)
            simulation_thread = threading.Thread(target=scatter.execute_simulation, args=(self.view.stop_optimization,))
            simulation_thread.start()

        if opt_method == "Scatter AI":
            scatter_ai = ScatterAI(self.view.app.repository, self.model)
            simulation_thread = threading.Thread(target=scatter_ai.execute_simulation, args=(self.view.stop_optimization,))
            simulation_thread.start()

        if opt_method == "GRASP":
            grasp = Grasp(self.view.app.repository, self.model)
            simulation_thread = threading.Thread(target=grasp.execute_simulation, args=(self.view.stop_optimization,))
            simulation_thread.start()

        if opt_method == "GRASP AI":
            grasp_ai = GraspAI(self.view.app.repository, self.model)
            simulation_thread = threading.Thread(target=grasp_ai.execute_simulation, args=(self.view.stop_optimization,))
            simulation_thread.start()

        if opt_method == "PSO":
            pso = PSO(self.view.app.repository, self.model)
            simulation_thread = threading.Thread(target=pso.execute_simulation, args=(self.view.stop_optimization,))
            simulation_thread.start()

        if opt_method == "Firefly":
            firefly = FSO(self.view.app.repository, self.model)
            simulation_thread = threading.Thread(target=firefly.execute_simulation, args=(self.view.stop_optimization,))
            simulation_thread.start()
            
    def update_repository(self):
        self.view.app.repository.best_values = self.model.best_values
        self.view.app.repository.best_values_set = self.model.best_values_set

    
    def rebuild_graph(self):
        self.model.graph = build_graph(self.view.app.repository)

    def previous_screen(self):
        self.update_repository()
        self.view.manager_screens.current = "define method screen"

    def update(self):
        self.update_repository()
        self.rebuild_graph()
        self.view.best_values = self.model.best_values
        self.view.best_values_set = self.model.best_values_set
        self.view.graph = self.model.graph