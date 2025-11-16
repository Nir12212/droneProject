from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class DataPage(Screen):
    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        # Main layout
        layout = FloatLayout()

        # Vertical box for labels
        label_box = BoxLayout(orientation='vertical', spacing=10,
                              size_hint=(0.4, 0.5), pos_hint={'x': 0.05, 'top': 0.9})
        self.tempLabel = Label(text="Temperature:", font_size=20, color=(1,1,1,1))
        self.humidityLabel = Label(text="Humidity:", font_size=20, color=(1,1,1,1))
        self.airPressureLabel = Label(text="Air Pressure:", font_size=20, color=(1,1,1,1))
        self.magneticFieldLabel = Label(text="Magnetic Field:", font_size=20, color=(1,1,1,1))

        label_box.add_widget(self.tempLabel)
        label_box.add_widget(self.humidityLabel)
        label_box.add_widget(self.airPressureLabel)
        label_box.add_widget(self.magneticFieldLabel)

        # Horizontal box for buttons at the bottom
        button_box = BoxLayout(orientation='horizontal', spacing=20,
                               size_hint=(0.6, 0.15), pos_hint={'center_x': 0.5, 'y': 0.05})
        showDataBtn = Button(text="Show Data", background_color=(0.5,0.8,1,1))
        backBtn = Button(text="Back", background_color=(0.5,0.8,1,1))
        showDataBtn.bind(on_press=self.getData)
        backBtn.bind(on_press=self.goBack)

        button_box.add_widget(backBtn)
        button_box.add_widget(showDataBtn)

        layout.add_widget(label_box)
        layout.add_widget(button_box)

        self.add_widget(layout)

    def deleteData(self):
        self.tempLabel.text = "Temperature:"
        self.humidityLabel.text = "Humidity:"
        self.airPressureLabel.text = "Air Pressure:"
        self.magneticFieldLabel.text = "Magnetic Field:"

    def goBack(self, instance):
        self.manager.current = "menu"
        self.deleteData()

    def getData(self, instance):
        if not self.controller:
            return

        data = self.controller.get_sensor_data()
        if "error" in data:
            self.deleteData()
            return

        self.tempLabel.text = f"Temperature: {data[0]}"
        self.humidityLabel.text = f"Humidity: {data[1]}"
        self.airPressureLabel.text = f"Air Pressure: {data[2]}"
        self.magneticFieldLabel.text = f"Magnetic Field: {data[3]}"
