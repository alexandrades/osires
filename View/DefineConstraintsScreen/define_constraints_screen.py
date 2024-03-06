from View.base_screen import BaseScreenView
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty, ObjectProperty, NumericProperty


class DefineConstraintsScreenView(BaseScreenView):
    constraint_list = ListProperty([])
    output_list = ListProperty([])

    def on_pre_enter(self):
        self.controller.set_initial_values()

    def on_output_list(self, instance, value):
        variables_list = self.ids.resource_list
        variables_list.clear_widgets()

        for i in self.output_list:
            variables_list.add_widget(ResourceListItem(i))

    def on_constraint_list(self, instance, value):
        self.ids.constraint_list.clear_widgets()

        for idx, constraint in enumerate(value):
            self.ids.constraint_list.add_widget(ConstraintItem(constraint_content=constraint, index=idx, callback=self.remove_constraint))

    def add_constraint(self):
        constraint_content = self.ids.text_field.ids.text_field.text
        if constraint_content not in self.constraint_list:
            self.constraint_list.append(constraint_content)
            self.model.constraint_list = self.constraint_list
        self.ids.text_field.ids.text_field.text = ""

    def remove_constraint(self, constraint):
        self.constraint_list.remove(constraint)
        self.model.constraint_list = self.constraint_list

    def previous_screen(self):
        self.controller.previous_screen()

    def next_screen(self):
        self.controller.next_screen()

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
        self.controller.update()


class ResourceListItem(MDLabel):
    def __init__(self, variable, **kwargs):
        super().__init__(**kwargs)
        self.text = variable
    pass


class ConstraintItem(MDBoxLayout):
    constraint_content = StringProperty()
    callback = ObjectProperty()
    index = NumericProperty()

    def __init__(self, constraint_content, index,  callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback
        self.constraint_content = constraint_content
        self.index = index

    def remove(self):
        self.callback(self.constraint_content)

    # def remove_constraint(self):
    #     self.parent.parent.parent.parent.parent.constraint_list.pop(self.constraint_index-1)
