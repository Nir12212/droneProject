import socket
import time


CAM_PIC_IP = "192.168.4.100"
PIC_PORT = 1235


class PictureModel:
    def __init__(self):
        self.images = []
        self.index = 0

    def receive_picture(self):
        filename = f"pic_{int(time.time())}.jpg"

        try:
            s = socket.socket()
            s.settimeout(5)
            s.connect((CAM_PIC_IP, PIC_PORT))

            with open(filename, "wb") as f:
                while True:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    f.write(chunk)

            s.close()

            self.images.append(filename)
            self.index = len(self.images) - 1
            return filename

        except Exception as e:
            print("Picture error:", e)
            return None
