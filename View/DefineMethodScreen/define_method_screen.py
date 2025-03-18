from View.base_screen import BaseScreenView
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import StringProperty
from kivymd.uix.label import MDLabel
from kivy.uix.spinner import Spinner
from kivymd.uix.textfield import MDTextField


class DefineMethodScreenView(BaseScreenView):
    opt_method = StringProperty("")
    opt_type = StringProperty("")
    ml_algorithm = StringProperty("")
    min_simulations_train = StringProperty("")
    save_path = ''

    def __init__(self, **kw):
        super().__init__(**kw)
        opt_method_spinner = self.ids.opt_method_spinner
        opt_method_spinner.bind(text=self.get_opt_method)
        opt_type_spinner = self.ids.opt_type_spinner
        opt_type_spinner.bind(text=self.get_opt_type)

    def on_pre_enter(self) -> None:
        self.controller.set_initial_values()

    def get_opt_method(self, spinner, text):
        self.opt_method = text
        self.model.opt_method = self.opt_method

        if "AI" in text:
            if len(self.ids.options_grid.children) > 4:
                return
            self.add_ai_options()
            return

        if len(self.ids.options_grid.children) > 4:
            self.remove_ai_options()

    def get_ml_algorithm(self, spinner, text):
        self.ml_algorithm = text
        print(self.ml_algorithm)
        self.model.ml_algorithm = self.ml_algorithm

    def get_opt_type(self, spinner, text):
        self.opt_type = text
        self.model.opt_type = self.opt_type

    def get_min_simulations_train(self, instance, value):
        self.min_simulations_train = value
        print(value)
        self.model.min_simulations_train = value

    def remove_ai_options(self):
        for child in self.ids.options_grid.children[0:4]:
            self.ids.options_grid.remove_widget(child)


    def add_ai_options(self):
        label_ml_algorithm = MDLabel(
            text= "Select AI method:",
            color= (0, 0, 0, 1),
            text_size= (self.width, None),
            halign= "left",
            size_hint= (1, None),
            height= 28,
            size_hint_x= 0.4
        )

        spinner_ml_algorithm = Spinner(
            text= self.ml_algorithm,
            values= ('RF', 'DT', 'KN', 'GP'),
            size_hint= (1, None),
            height= 28,
            sync_height= True
        )

        label_min_simulations = MDLabel(
            text="Min. AI Training Dataset Size:",
            color= (0, 0, 0, 1),
            text_size= (self.width, None),
            halign= "left",
            size_hint= (1, None),
            height= 28,
            size_hint_x= 0.4
        )

        input_min_simulations_train = MDTextField(
            size_hint=(1, None),
            height=28,
            hint_text="Minimum 100 by 100",
            text=self.min_simulations_train
        )

        spinner_ml_algorithm.bind(text=self.get_ml_algorithm)
        input_min_simulations_train.bind(text=self.get_min_simulations_train)
        spinner_ml_algorithm.id = "ml_algorithm_spinner"
        spinner_ml_algorithm.id = "minumum_simulations_input"
        self.ids.options_grid.add_widget(label_ml_algorithm)
        self.ids.options_grid.add_widget(spinner_ml_algorithm)
        self.ids.options_grid.add_widget(label_min_simulations)
        self.ids.options_grid.add_widget(input_min_simulations_train)

    def run_opt(self):
        self.controller.run_opt()

    def previous_screen(self):
        self.controller.previous_screen()

    def save_opt_options(self):
        self.controller.save_opt_options()


    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
        
