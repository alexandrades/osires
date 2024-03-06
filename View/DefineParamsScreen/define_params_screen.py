from functools import partial
from View.base_screen import BaseScreenView
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, DictProperty, ObjectProperty
import os

class ResourceItem(MDBoxLayout):
    resource_name = StringProperty("")
    resource_params = DictProperty({})
    minimum_value = StringProperty("")
    maximum_value = StringProperty("")
    step_value = StringProperty("")
    initial_value = StringProperty("")
    callback = ObjectProperty()

    def __init__(self, resource_name, resource_params, callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource_name = resource_name
        self.resource_params = resource_params
        self.minimum_value = str(resource_params['minimum_value'])
        self.maximum_value = str(resource_params['maximum_value'])
        self.step_value = str(resource_params['step_value'])
        self.initial_value = str(resource_params['initial_value'])
        self.callback = callback
        self.ids.resource_minimum_value.bind(text=partial(callback, resource=resource_name, param='minimum_value'))
        self.ids.resource_maximum_value.bind(text=partial(callback, resource=resource_name, param='maximum_value'))
        self.ids.resource_step_value.bind(text=partial(callback, resource=resource_name, param='step_value'))
        self.ids.resource_initial_value.bind(text=partial(callback, resource=resource_name, param='initial_value'))


class DefineParamsScreenView(BaseScreenView):

    resource_list = DictProperty({})
    resources_names = []

    def __init__(self, **kw):
        super().__init__(**kw)
        self.callback = self.controller.update_params

    def on_pre_enter(self) -> None:
        self.resources_names = self.controller.get_resources_names()
        self.controller.set_initial_values()
        print("Resources =======================", self.resource_list)
        self.add_resources()


    def add_resources(self):
        if len(self.ids.resource_list.children) > 2:
            print("+++++++++\n\n++++++++++")
            return
        
        if self.resource_list == {}:
            for resource in self.resources_names:
                self.resource_list[resource] = {'minimum_value': '', 'maximum_value': '', 'step_value': '', 'initial_value': ''}
            self.model.resources_list = self.resource_list

        for resource in self.resources_names:
            self.ids.resource_list.add_widget(
                ResourceItem(resource_name=resource, resource_params=self.resource_list[resource], callback=self.callback)
            )

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

