from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
import socket
import json
 

ESP_IP = "192.168.4.1"
DATA_PORT = 1234
PIC_PORT = 1235
#MAIN MENU
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
#   DATA PAGE
class DataPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        self.tempLabel = Label(
            text="Temperature:",
            color=(1, 1, 1, 1),
            font_size=20,
            size_hint=(None, None),
            pos_hint={'x': 0.05, 'y': 0.85}
        )
        self.humidityLabel = Label(
            text = "Humidity:",
            color=(1, 1, 1, 1),
            font_size=20,
            size_hint=(None, None),
            pos_hint={'x': 0.03, 'y': 0.75}
        )
        self.airPressureLabel = Label(
            text = "Air Pressure:",
            color=(1, 1, 1, 1),
            font_size=20,
            size_hint=(None, None),
            pos_hint={'x': 0.05, 'y': 0.65}
        )
        self.magneticFieldLabel = Label(
            text = "Magnetic Field:",
            color=(1, 1, 1, 1),
            font_size=20,
            size_hint=(None, None),
            pos_hint={'x': 0.06, 'y': 0.55}
        )
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
        showDataBtn.bind(on_press=self.getData)

        layout.add_widget(self.tempLabel)
        layout.add_widget(self.humidityLabel)
        layout.add_widget(self.airPressureLabel)
        layout.add_widget(self.magneticFieldLabel)
        layout.add_widget(showDataBtn)
        layout.add_widget(backBtn)
        
        self.add_widget(layout)



    def getData(self,instance):
        try:
            s = socket.socket()
            s.settimeout(3)
            s.connect((ESP_IP, DATA_PORT))
            s.send(b"requestData\n")
            data = s.recv(1024)
            s.close()
            msg = data.decode()
            data = json.loads(msg)
            self.tempLabel.text = f"Temperature: {data[0]}"
            self.humidityLabel.text = f"Humidity: {data[1]}"
            self.airPressureLabel.text = f"Air Pressure: {data[2]}"
            self.magneticFieldLabel.text = f"Magnetic Field: {data[3]}"
        except Exception as e:
            msg = f"Error: {e}"
            self.tempLabel.text = "Temperature:"
            self.humidityLabel.text = "Humidity:"
            self.airPressureLabel.text = "Air Pressure:"
            self.magneticFieldLabel.text = f"Magnetic Field:"

        print(msg)
    



    def goBack(self, instance):
        self.manager.current = "menu"

# PICTURES PAGE 
class PicturesPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.imageArray = []
        self.imageNum = 0
        self.image = Image(
            source = self.imageArray[self.imageNum],
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.8, 0.8),
            pos_hint={'x':0.1, 'y':0.1}
        )


        showBtn = Button(
            text="Show Image",
            size_hint=(None, None),
            size=(200, 80),
            pos_hint={'x': 0.5, 'y': 0.05},
        )
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

        rightBtn.bind(on_press=self.nextPic)
        leftBtn.bind(on_press=self.prevPic)
        backBtn.bind(on_press=self.goBack)
        showBtn.bind(on_press=self.showImage)

        
        self.layout.add_widget(leftBtn)
        self.layout.add_widget(rightBtn)
        self.layout.add_widget(backBtn)
        self.layout.add_widget(showBtn)
        self.add_widget(self.layout)




    def nextPic(self,instance):
        if len(self.imageArray)>0 and self.image in self.layout.children:
            self.imageNum= (self.imageNum + 1) % len(self.imageArray)
            self.image.source = self.imageArray[self.imageNum]
            self.image.reload()
    def prevPic(self,instance):
        if len(self.imageArray)>0:
            self.imageNum= (self.imageNum - 1) % len(self.imageArray)
            self.image.source = self.imageArray[self.imageNum]
            self.image.reload()

    def goBack(self, instance):
        self.manager.current = "menu"
    def showImage(self, instance):
        self.imageArray.append(self.getPicture())
        if not(self.image in self.layout.children):
           self.layout.add_widget(self.image)
    def getPicture(self):

        try:
            # Create a unique filename
            filename = f"received_{len(self.imageArray)}.jpg"

            # Connect to the ESP32 image socket
            s = socket.socket()
            s.settimeout(5)
            s.connect((ESP_IP, PIC_PORT))
            print("Connected to image server. Receiving image...")

            # Receive the file in chunks
            with open(filename, "wb") as f:
                while True:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    f.write(chunk)

            s.close()
            print(f"Image saved as {filename}")
            return filename

        except Exception as e:
            print("Error receiving image:", e)
            return None

        
            

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
