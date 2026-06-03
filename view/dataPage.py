from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class DataPage(Screen):
    def _init_(self, controller=None, **kwargs):
        super()._init_(**kwargs)
        self.controller = controller

        layout = FloatLayout()

        # ===== LABELS =====
        label_box = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint=(0.4, 0.5),
            pos_hint={'x': 0.05, 'top': 0.9}
        )

        def create_label(text):
            return Label(
                text=text,
                font_size=20,
                color=(1,1,1,1),
                halign='left',
                valign='middle',
                size_hint=(None, None),
                width=300,  # fixed width
                height=30,
                text_size=(300, None)  # important for halign
            )

        # Create all labels
        self.tempLabel = create_label("Temperature:")
        self.humidityLabel = create_label("Humidity:")
        self.airPressureLabel = create_label("Air Pressure:")
        self.magneticFieldLabel = create_label("Magnetic Field:")
        self.xAxisLabel = create_label("X:")
        self.yAxisLabel = create_label("Y:")
        self.zAxisLabel = create_label("Z:")

        # Add labels to layout
        for lbl in (self.tempLabel, self.humidityLabel, self.airPressureLabel,
                    self.magneticFieldLabel, self.xAxisLabel, self.yAxisLabel, self.zAxisLabel):
            label_box.add_widget(lbl)

        # ===== BUTTONS =====
        button_box = BoxLayout(
            orientation='horizontal',
            spacing=20,
            size_hint=(0.6, 0.15),
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )

        backBtn = Button(text="Back", background_color=(0.5, 0.8, 1, 1))
        showDataBtn = Button(text="Show Data", background_color=(0.5, 0.8, 1, 1))

        backBtn.bind(on_press=self.goBack)
        showDataBtn.bind(on_press=self.getData)

        button_box.add_widget(backBtn)
        button_box.add_widget(showDataBtn)

        layout.add_widget(label_box)
        layout.add_widget(button_box)
        self.add_widget(layout)

    # ===== FUNCTIONS =====
    def deleteData(self):
        self.tempLabel.text = "Temperature:"
        self.humidityLabel.text = "Humidity:"
        self.airPressureLabel.text = "Air Pressure:"
        self.magneticFieldLabel.text = "Magnetic Field:"
        self.xAxisLabel.text = "X:"
        self.yAxisLabel.text = "Y:"
        self.zAxisLabel.text = "Z:"

    def goBack(self, instance):
        self.manager.current = "menu"
        self.deleteData()

    def getData(self, instance=None):
        if not self.controller:
            return

        data = self.controller.get_sensor_data()

        if not data or "error" in data:
            self.tempLabel.text = "Temperature: Sensor error"
            self.humidityLabel.text = "Humidity: Sensor error"
            self.airPressureLabel.text = "Air Pressure: Sensor error"
            self.magneticFieldLabel.text = "Magnetic Field: Sensor error"
            self.xAxisLabel.text = "X: Sensor error"
            self.yAxisLabel.text = "Y: Sensor error"
            self.zAxisLabel.text = "Z: Sensor error"
            return

        self.tempLabel.text = f"Temperature: {data[0]} C"
        self.humidityLabel.text = f"Humidity: {data[1]} %"
        self.airPressureLabel.text = f"Air Pressure: {data[2]} "
        self.magneticFieldLabel.text = f"Magnetic Field: {data[6]} uT "
        self.xAxisLabel.text = f"X: {data[3]} uT"
        self.yAxisLabel.text = f"Y: {data[4]} uT"
        self.zAxisLabel.text = f"Z: {data[5]} uT"
