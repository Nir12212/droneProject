import socket
import struct
import threading
from kivy.clock import Clock


CAM_STREAM_IP = "192.168.4.101"
STREAM_PORT = 1236


class StreamModel:
    def start_stream(self, update_callback):
        thread = threading.Thread(target=self._stream_loop, args=(update_callback,), daemon=True)
        thread.start()

    def _stream_loop(self, callback):
        try:
            s = socket.socket()
            s.connect((CAM_STREAM_IP, STREAM_PORT))

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

                Clock.schedule_once(lambda dt, fn=filename: callback(fn))

        except Exception as e:
            print("Stream error:", e)
