from View.base_screen import BaseScreenView
from kivymd.uix.tab.tab import MDTabsBase
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from plyer import filechooser
import json
import os

class Tab(MDBoxLayout, MDTabsBase):
    pass

class TextFieldIconButton(MDBoxLayout):
    text = StringProperty()
    hint_text = StringProperty()
    label_text = StringProperty()
    callback = None
    icon = StringProperty()

        


class MainScreenView(BaseScreenView):

    osires_file = StringProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.osires_file = self.model.osires_file
    
    def get_osires_file_path(self):
        self.text = self.controller.get_osires_file_path()

    def creste_new_optimization(self):
        self.controller.creste_new_optimization()


    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

        self.controller.update()
