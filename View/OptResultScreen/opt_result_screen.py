from View.base_screen import BaseScreenView
from kivy.properties import StringProperty, DictProperty, NumericProperty
import threading


class OptResultScreenView(BaseScreenView):
    best_values = DictProperty({'Params': [], 'Value': ''})
    stop_optimization = threading.Event()

    def on_pre_enter(self) -> None:
        self.controller.set_initial_values()
        self.controller.init_optimization()

    def stop_opt(self):
        self.ids.simulation_status.text = "Status: Finalizado"
        self.stop_optimization.set()

    def previous_screen(self):
        self.controller.previous_screen()

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
