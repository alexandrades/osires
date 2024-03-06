from View.base_screen import BaseScreenView
from kivy.properties import StringProperty


class SelectModelScreenView(BaseScreenView):
    # REMOVER VALOR PADRÃO NO FINAL
    model_file_path = StringProperty("")
    input_file_path = StringProperty("")
    output_file_path = StringProperty("")

    # def __init__(self, **kw):
    #     super().__init__(**kw)
    #     self.model_file_path = self.app

    def on_pre_enter(self) -> None:
        self.controller.set_initial_values(self)
        print("Osires file", self.app.repository.osires_file)

    def get_model_file_path(self) -> None:
        self.controller.get_model_file_path()

    def get_input_file_path(self) -> None:
        self.controller.get_input_file_path()

    def get_output_file_path(self) -> None:
        self.controller.get_output_file_path()

    def previous_screen(self) -> None:
        self.controller.previous_screen()

    def next_screen(self) -> None:
        self.controller.next_screen()

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
        # self.controller.update()
        if self.model_file_path != '' and self.input_file_path != '' and self.output_file_path != '':
            self.ids.next_button.disabled = False