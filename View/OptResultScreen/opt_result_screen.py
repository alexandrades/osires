import kivy
from View.base_screen import BaseScreenView
from kivy.properties import StringProperty, DictProperty, NumericProperty
from kivy_garden.matplotlib import FigureCanvasKivyAgg
from kivy.clock import Clock
import threading
import logging
logging.basicConfig(level=logging.WARNING)

class OptResultScreenView(BaseScreenView):
    best_values = DictProperty({'Params': [], 'Value': ''})
    best_values_set = DictProperty({'Values': [], 'Interactions': []})
    graph = {}
    stop_optimization = threading.Event()

    def on_pre_enter(self) -> None:
        self.controller.set_initial_values()
        Clock.schedule_interval(self.graph_reload, 1.0 / 60.0)
        self.controller.init_optimization()    
    
    def graph_reload(self, dt):
        self.ids.graph.clear_widgets()
        self.ids.graph.add_widget(FigureCanvasKivyAgg(self.graph))


    def stop_opt(self):
        self.ids.simulation_status.text = "Status: Finalizado"
        self.stop_optimization.set()

    def previous_screen(self):
        self.stop_opt()
        self.controller.previous_screen()

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
