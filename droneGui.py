from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout


# MAIN MENU
class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="horizontal", padding=20, spacing=15)

        
        dataBtn = Button(
            text="DATA",
            size_hint=(None, None),
            size=(150, 80),
            font_size=20,
            color=(1, 1, 1, 1),
            background_color=(0, 0.5, 1, 1)
        )

        
        picBtn = Button(
            text="PICTURES",
            size_hint=(None, None),
            size=(150, 80),
            font_size=20,
            color=(1, 1, 1, 1),
            background_color=(0, 0.5, 1, 1)
        )

        
        picBtn.bind(on_press=self.goShowPicsPage)
        dataBtn.bind(on_press=self.goDataPage)

        
        layout.add_widget(dataBtn)
        layout.add_widget(picBtn)
        self.add_widget(layout)

    
    def goDataPage(self, instance):
        self.manager.current = "data"

    
    def goShowPicsPage(self, instance):
        self.manager.current = "pics"  


# DATA PAGE
class DataPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        showDataBtn = Button(
            text="show data",
            size_hint=(None, None),
            size=(200, 80),
            pos_hint={'x': 0.5, 'y': 0.05},
            background_color=(0, 0.5, 1, 1)
        )

        backBtn = Button(
            text="back",
            size_hint=(None, None),
            size=(70, 80),
            pos_hint={'x': 0.10, 'y': 0.05},
            background_color=(0, 0.5, 1, 1)
        )
        backBtn.bind(on_press=self.goBack)

        layout.add_widget(showDataBtn)
        layout.add_widget(backBtn)
        self.add_widget(layout)

    def goBack(self,instance):
        self.manager.current = "menu"

# PICTURES PAGE
class PicturesPage(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        layout=FloatLayout()

        leftBtn = Button(
            text="<-",
            size_hint=(None, None),
            size=(70, 80),
            pos_hint={'x': 0.10, 'y': 0.5},
            background_color=(0, 0.5, 1, 1)
        )

        rightBtn = Button(
            text="->",
            size_hint=(None, None),
            size=(70, 80),
            pos_hint={'x': 0.20, 'y': 0.5},
            background_color=(0, 0.5, 1, 1)
        )
        backBtn = Button(
            text="back",
            size_hint=(None, None),
            size=(70, 80),
            pos_hint={'x': 0.1, 'y': 0.05},
            background_color=(0, 0.5, 1, 1)

        )
        backBtn.bind(on_press=self.goBack)
        layout.add_widget(leftBtn)
        layout.add_widget(rightBtn)
        layout.add_widget(backBtn)
        self.add_widget(layout)
    def goBack(self,instance):
        self.manager.current = "menu"
#  APP 
class droneGui(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="menu"))
        sm.add_widget(DataPage(name="data"))
        sm.add_widget(PicturesPage(name="pics"))
        return sm


#  RUN 
if __name__ == "__main__":
    droneGui().run()
