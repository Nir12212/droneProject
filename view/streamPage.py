from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.image import Image

class StreamPage(Screen):
    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        # Main vertical layout
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Anchor layout to center the image
        img_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.8))
        self.stream_img = Image(allow_stretch=True, keep_ratio=True)
        img_anchor.add_widget(self.stream_img)

        # Bottom button bar
        button_box = BoxLayout(orientation='horizontal', spacing=20,
                               size_hint=(1, 0.15), padding=[20,0,20,0])
        back_btn = Button(text="Back", background_color=(0.5,0.8,1,1))
        start_btn = Button(text="Start Stream", background_color=(0.5,0.8,1,1))

        back_btn.bind(on_press=self.go_back)
        start_btn.bind(on_press=self.start_stream)

        button_box.add_widget(back_btn)
        button_box.add_widget(start_btn)

        layout.add_widget(img_anchor)
        layout.add_widget(button_box)
        self.add_widget(layout)

    def start_stream(self, instance):
        if self.controller:
            self.controller.start_stream(self.update_image)

    def update_image(self, filename):
        self.stream_img.source = filename
        self.stream_img.reload()

    def go_back(self, instance):
        self.manager.current = "menu"
