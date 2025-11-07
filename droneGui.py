from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
import socket
import json
import time
import struct
from PIL import Image as PILImage
import io
import threading
from kivy.clock import Clock

ESP_IP = "192.168.4.1"
DATA_PORT = 1234
PIC_PORT = 1235
STREAM_PORT = 1236
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
        streamBtn = Button(
            text="STREAM",
            size_hint=(None, None),
            size=(150, 80),
            font_size=20,
            color=(1, 1, 1, 1),
            background_color=(0, 0.5, 1, 1)
        )
        picBtn.bind(on_press=self.goShowPicsPage)
        dataBtn.bind(on_press=self.goDataPage)
        streamBtn.bind(on_press=self.goStreamPage)

        layout.add_widget(dataBtn)
        layout.add_widget(picBtn)
        layout.add_widget(streamBtn)
        self.add_widget(layout)

    def goStreamPage(self,instance):
        self.manager.current = "stream"
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
        self.imageWidget = Image(allow_stretch=True, keep_ratio=True, size_hint=(0.8, 0.8), pos_hint={'x':0.1, 'y':0.1})

        showBtn = Button(text="Show Image", size_hint=(None, None), size=(200, 80), pos_hint={'x':0.5, 'y':0.05})
        leftBtn = Button(text="<-", size_hint=(None, None), size=(70, 80), pos_hint={'x':0.05, 'y':0.5})
        rightBtn = Button(text="->", size_hint=(None, None), size=(70, 80), pos_hint={'x':0.20, 'y':0.5})
        backBtn = Button(text="Back", size_hint=(None, None), size=(70, 80), pos_hint={'x':0.1, 'y':0.05})

        showBtn.bind(on_press=self.getPicture)
        leftBtn.bind(on_press=self.prevPic)
        rightBtn.bind(on_press=self.nextPic)
        backBtn.bind(on_press=self.goBack)

        self.layout.add_widget(showBtn)
        self.layout.add_widget(leftBtn)
        self.layout.add_widget(rightBtn)
        self.layout.add_widget(backBtn)
        self.add_widget(self.layout)

    def getPicture(self, instance=None):
        filename = f"pic_{int(time.time())}.jpg"
        try:
            s = socket.socket()
            s.settimeout(5)
            s.connect((ESP_IP, PIC_PORT))

            with open(filename, "wb") as f:
                while True:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    f.write(chunk)
            s.close()
            print(f"Saved image as {filename}")

            # Add to the list and show
            self.imageArray.append(filename)
            self.imageNum = len(self.imageArray) - 1
            self.showImage()

        except Exception as e:
            print("Error receiving picture:", e)

    def showImage(self):
        if len(self.imageArray) > 0:
            self.imageWidget.source = self.imageArray[self.imageNum]
            if self.imageWidget not in self.layout.children:
                self.layout.add_widget(self.imageWidget)
            self.imageWidget.reload()

    def nextPic(self, instance):
        if len(self.imageArray) > 0:
            self.imageNum = (self.imageNum + 1) % len(self.imageArray)
            self.showImage()

    def prevPic(self, instance):
        if len(self.imageArray) > 0:
            self.imageNum = (self.imageNum - 1) % len(self.imageArray)
            self.showImage()

    def goBack(self, instance):
        self.manager.current = "menu"


class StreamPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()

        # Image widget
        self.stream_image = Image(
            allow_stretch=False,
            keep_ratio=True,
            size_hint=(0.8, 0.8),
            pos_hint={'x': 0.1, 'y': 0.15}
        )

        # Start button
        startBtn = Button(
            text="start",
            size_hint=(None, None),
            size=(200, 80),
            pos_hint={'x': 0.60, 'y': 0.05},
            background_color=(0, 0.5, 1, 1)
        )

        # Back button
        backBtn = Button(
            text="back",
            size_hint=(None, None),
            size=(70, 80),
            pos_hint={'x': 0.10, 'y': 0.05},
            background_color=(0, 0.5, 1, 1)
        )

        # Bind buttons
        backBtn.bind(on_press=self.goBack)
        startBtn.bind(on_press=self.start_streaming)

        # Add widgets
        self.layout.add_widget(startBtn)
        self.layout.add_widget(backBtn)
        self.layout.add_widget(self.stream_image)
        self.add_widget(self.layout)

    def goBack(self, instance):
        self.manager.current = "menu"

    def start_streaming(self, instance):
        # Run streaming in a separate thread
        threading.Thread(target=self.stream_thread, daemon=True).start()

    def stream_thread(self):
        try:
            s = socket.socket()
            s.connect((ESP_IP, STREAM_PORT))
            while True:
                size_data = s.recv(4)
                if not size_data:
                    break
                size = struct.unpack("<L", size_data)[0]

                buf = b""
                while len(buf) < size:
                    buf += s.recv(size - len(buf))

                filename = "temp_stream.jpg"
                with open(filename, "wb") as f:
                    f.write(buf)

                # Schedule update on the main thread
                Clock.schedule_once(lambda dt, fn=filename: self.update_image(fn))
        except Exception as e:
            print("Stream error:", e)
        finally:
            s.close()

    def update_image(self, filename):
        self.stream_image.source = filename
        self.stream_image.reload()


            
class DroneGui(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="menu"))
        sm.add_widget(DataPage(name="data"))
        sm.add_widget(PicturesPage(name="pics"))
        sm.add_widget(StreamPage(name="stream"))

        return sm

#  RUN 
if __name__ == "__main__":
    DroneGui().run()
