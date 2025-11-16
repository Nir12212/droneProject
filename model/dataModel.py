import socket
import json


ESP_IP = "192.168.4.1"
DATA_PORT = 1234


class DataModel:
    def fetch_data(self):
        try:
            s = socket.socket()
            s.settimeout(3)
            s.connect((ESP_IP, DATA_PORT))
            s.send(b"requestData\n")
            msg = s.recv(1024).decode()
            s.close()
            return json.loads(msg)
        except Exception as e:
            return {"error": str(e)}
