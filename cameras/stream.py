import network
import socket
import struct
import time
import camera



# -------------------- CONFIG --------------------
MASTER_AP_SSID = "MY_WIFI"      # AP SSID
MASTER_AP_PASSWORD = "12345678" # AP password
STREAM_PORT = 1236
CONNECT_TIMEOUT = 15

# seconds
IP = "192.168.4.101"      # pick an unused IP in your AP subnet
SUBNET = "255.255.255.0"
GATEWAY = "192.168.4.1"   # usually your AP’s IP
DNS = "192.168.4.1"
# -------------------- CONNECT TO MASTER AP --------------------
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.ifconfig((IP, SUBNET, GATEWAY, DNS))
time.sleep(0.5)  # Give Wi-Fi driver time to initialize

print("Connecting to AP...")
sta.connect(MASTER_AP_SSID, MASTER_AP_PASSWORD)

start_time = time.time()
while not sta.isconnected():
    if time.time() - start_time > CONNECT_TIMEOUT:
        print("Failed to connect to AP! Check SSID, password, and channel.")
        raise SystemExit
    print("Connecting...")
    time.sleep(0.5)

print("Connected to AP. STA IP:", sta.ifconfig()[0])

# -------------------- SETUP CAMERA --------------------
try:
    camera.deinit()
except:
    pass

camera.init(0, format=camera.JPEG)
camera.framesize(camera.FRAME_QVGA)  # 320x240
camera.quality(14)                   # JPEG compression

# -------------------- START TCP STREAMING SERVER --------------------
def start_stream_server(port):
    while True:
        try:
            s = socket.socket()
            s.bind(("0.0.0.0", port))
            s.listen(1)
            s.settimeout(1)
            print(f"Waiting for client on port {port}...")
            
            conn, addr = s.accept()
            print("Client connected from", addr)
            conn.settimeout(2)
            
            while True:
                buf = camera.capture()
                if not buf:
                    continue

                size = len(buf)
                # Send frame size first (4 bytes, little-endian)
                conn.send(struct.pack("<L", size))
                # Then send the image
                conn.send(buf)

                time.sleep(0.1)  # ~10 FPS

        except OSError as e:
            print("Connection error or client disconnected:", e)
        except Exception as e:
            print("Unexpected error:", e)
        finally:
            try:
                conn.close()
            except:
                pass
            try:
                s.close()
            except:
                pass
            print("Server restarting in 2s...")
            time.sleep(2)

# -------------------- RUN --------------------
start_stream_server(STREAM_PORT)

