import socket
import struct
import threading
from kivy.clock import Clock

CAM_STREAM_IP = "192.168.4.101"
STREAM_PORT = 1236


class StreamModel:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = None

    def start_stream(self, update_callback):
        """Start the video streaming thread."""
        if self.thread and self.thread.is_alive():
            return  # already running

        self.stop_event.clear()

        self.thread = threading.Thread(
            target=self._stream_loop, 
            args=(update_callback,), 
            daemon=True
        )
        self.thread.start()

    def stop_stream(self, update_callback=None):
        """Stop the video streaming thread safely."""
        self.stop_event.set()

        if self.thread:
            self.thread.join()
            self.thread = None

    def _stream_loop(self, callback):
        try:
            s = socket.socket()
            s.connect((CAM_STREAM_IP, STREAM_PORT))
            s.settimeout(1)

            while not self.stop_event.is_set():

                # Try to read frame size
                try:
                    size_data = s.recv(4)
                    if not size_data:
                        break
                except:
                    continue

                size = struct.unpack("<L", size_data)[0]

                buf = b""
                while len(buf) < size and not self.stop_event.is_set():
                    chunk = s.recv(size - len(buf))
                    if not chunk:
                        break
                    buf += chunk

                if self.stop_event.is_set():
                    break

                filename = "temp_stream.jpg"
                with open(filename, "wb") as f:
                    f.write(buf)

                Clock.schedule_once(lambda dt, fn=filename: callback(fn))

        except Exception as e:
            print("Stream error:", e)

        finally:
            try:
                s.close()
            except:
                pass
