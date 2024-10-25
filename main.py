
"""
Script for managing hot reloading of the project.
For more details see the documentation page -

https://kivymd.readthedocs.io/en/latest/api/kivymd/tools/patterns/create_project/

To run the application in hot boot mode, execute the command in the console:
DEBUG=1 python main.py
"""

import importlib
import os

from kivy import Config
Config.set("graphics", "width", "850")
from kivy.core.window import Window
from kivymd.tools.hotreload.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import NoTransition, ScreenManager
from Utility.config_handler import OsiresFileHandler
from kivy.clock import Clock



class Osires(MDApp):
    KV_DIRS = [os.path.join(os.getcwd(), "View")]
    repository = OsiresFileHandler()


    def build_app(self) -> ScreenManager:
        """
        In this method, you don't need to change anything other than the
        application theme.
        """

        import View.screens
        

        self.manager_screens = ScreenManager(transition=NoTransition())
        Window.bind(on_key_down=self.on_keyboard_down)
        importlib.reload(View.screens)
        screens = View.screens.screens


        for i, name_screen in enumerate(screens.keys()):
            model = screens[name_screen]["model"]()
            controller = screens[name_screen]["controller"](model)
            view = controller.get_view()
            view.manager_screens = self.manager_screens
            view.name = name_screen
            self.manager_screens.add_widget(view)

        return self.manager_screens

    def on_keyboard_down(self, window, keyboard, keycode, text, modifiers) -> None:
        """
        The method handles keyboard events.

        By default, a forced restart of an application is tied to the
        `CTRL+R` key on Windows OS and `COMMAND+R` on Mac OS.
        """
        #Uncomment the line below to able the hot reload
        #if "meta" in modifiers or "ctrl" in modifiers and text == "r":
            #self.rebuild()


Osires().run()