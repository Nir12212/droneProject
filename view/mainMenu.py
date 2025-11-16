from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class MainMenu(Screen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        layout = BoxLayout(orientation="horizontal", spacing=20, size_hint=(None, None))
        layout.size = (500, 100)

        dataBtn = Button(
            text="DATA",
            size_hint=(None, None),
            size=(150, 80),
            font_size=20,
            color=(1, 1, 1, 1),
            background_color=(0.5, 0.8, 1, 1)
        )

        picsBtn = Button(
            text="PICTURES",
            size_hint=(None, None),
            size=(150, 80),
            font_size=20,
            color=(1, 1, 1, 1),
            background_color=(0.5, 0.8, 1, 1)
        )

        streamBtn = Button(
            text="STREAM",
            size_hint=(None, None),
            size=(150, 80),
            font_size=20,
            color=(1, 1, 1, 1),
            background_color=(0.5, 0.8, 1, 1)
        )

        # Bind buttons to methods
        dataBtn.bind(on_press=self.go_data)
        picsBtn.bind(on_press=self.go_pics)
        streamBtn.bind(on_press=self.go_stream)

        layout.add_widget(dataBtn)
        layout.add_widget(picsBtn)
        layout.add_widget(streamBtn)

        anchor.add_widget(layout)
        self.add_widget(anchor)

    # Methods to switch screens
    def go_data(self, instance):
        self.manager.current = "data"

    def go_pics(self, instance):
        self.manager.current = "pics"

    def go_stream(self, instance):
        self.manager.current = "stream"
