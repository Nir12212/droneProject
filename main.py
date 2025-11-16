from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

# Import your controller
from controller import DroneController

# Import your screens
from view.mainMenu import MainMenu
from view.dataPage import DataPage
from view.picturesPage import PicturesPage
from view.streamPage import StreamPage


Window.size = (800, 480)

class DroneGui(App):
    def build(self):
        # Create the controller
        self.controller = DroneController()

        # Create ScreenManager
        sm = ScreenManager()

        # Add all screens, passing the controller to each
        sm.add_widget(MainMenu(name="menu", controller=self.controller))
        sm.add_widget(DataPage(name="data", controller=self.controller))
        sm.add_widget(PicturesPage(name="pics", controller=self.controller))
        sm.add_widget(StreamPage(name="stream", controller=self.controller))

        # Return the ScreenManager to run the app
        return sm


if __name__ == "__main__":
    DroneGui().run()
