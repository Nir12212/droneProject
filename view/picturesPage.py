from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout

class PicturesPage(Screen):
    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.imageArray = []  # List of downloaded images
        self.imageNum = 0     # Current image index

        self.layout = FloatLayout()

        # Main image
        self.img = Image(
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.8, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.55}
        )
        self.layout.add_widget(self.img)

        # Left and right arrows
        leftBtn = Button(
            text="<-",
            size_hint=(0.08, 0.1),
            pos_hint={'x': 0.01, 'center_y': 0.55},
            background_color=(0.5, 0.8, 1, 1)
        )
        rightBtn = Button(
            text="->",
            size_hint=(0.08, 0.1),
            pos_hint={'right': 0.99, 'center_y': 0.55},
            background_color=(0.5, 0.8, 1, 1)
        )
        leftBtn.bind(on_press=self.prev_image)
        rightBtn.bind(on_press=self.next_image)
        self.layout.add_widget(leftBtn)
        self.layout.add_widget(rightBtn)

        # Bottom buttons: Back and Get Image
        bottom_box = BoxLayout(
            orientation='horizontal',
            spacing=20,
            size_hint=(0.8, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.025}
        )
        backBtn = Button(text="Back", background_color=(0.5,0.8,1,1))
        showBtn = Button(text="Get Image", background_color=(0.5,0.8,1,1))
        backBtn.bind(on_press=self.go_back)
        showBtn.bind(on_press=self.get_image)
        bottom_box.add_widget(backBtn)
        bottom_box.add_widget(showBtn)
        self.layout.add_widget(bottom_box)

        self.add_widget(self.layout)

    def get_image(self, instance):
        if not self.controller:
            return
        filename = self.controller.get_picture()
        if filename:
            self.imageArray.append(filename)
            self.imageNum = len(self.imageArray) - 1
            self.show_image()

    def show_image(self):
        if self.imageArray:
            self.img.source = self.imageArray[self.imageNum]
            self.img.reload()

    def next_image(self, instance):
        if self.imageArray:
            self.imageNum = (self.imageNum + 1) % len(self.imageArray)
            self.show_image()

    def prev_image(self, instance):
        if self.imageArray:
            self.imageNum = (self.imageNum - 1) % len(self.imageArray)
            self.show_image()

    def go_back(self, instance):
        if self.manager:
            self.manager.current = "menu"
