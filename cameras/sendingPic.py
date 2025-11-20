import network
import camera
import socket
import time

IP = "192.168.4.100"      # pick an unused IP in your AP subnet
SUBNET = "255.255.255.0"
GATEWAY = "192.168.4.1"   # usually your AP’s IP
DNS = "192.168.4.1"
# -------------------- CONFIGURATION --------------------
SSID = "MY_WIFI"
PASSWORD = "12345678"
PIC_PORT = 1235

# -------------------- SETUP ACCESS POINT --------------------
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.ifconfig((IP, SUBNET, GATEWAY, DNS))
sta.connect(SSID, PASSWORD)
print("good")
while not sta.isconnected():
    time.sleep(0.5)

cam_ip = sta.ifconfig()[0]
print("Camera connected to AP. STA IP:", cam_ip)

# -------------------- CAMERA CAPTURE & SEND --------------------
def capture_and_send(conn):
    """Capture an image from the camera and send it via the socket connection."""
    try:
        # Initialize camera in JPEG mode using PSRAM
        camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
        camera.quality(10)
        time.sleep(1)  # Allow camera to stabilize

        # Capture image
        buf = camera.capture()
        print("Captured image:", len(buf), "bytes")

        # Send image bytes to client
        conn.sendall(buf)
        print("Image sent to client.")

    except Exception as e:
        print("Camera error:", e)

    finally:
        camera.deinit()

# -------------------- SOCKET SERVER --------------------
s = socket.socket()
s.bind(('0.0.0.0', PIC_PORT))
s.listen(1)
print(f"Image server running on port {PIC_PORT}")

# -------------------- MAIN LOOP --------------------
while True:
    try:
        conn, addr = s.accept()
        print("Client connected:", addr)
        capture_and_send(conn)
        conn.close()
        print("Client disconnected")
    except OSError:
        # No client connected, continue listening
        pass
    except Exception as e:
        print("Server error:", e)
        time.sleep(1)
