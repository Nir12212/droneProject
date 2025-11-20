import network
import time
import socket
import ujson
import sensors 
# -------------------- CONFIG --------------------
SSID = "MY_WIFI"
PASSWORD = "12345678"
CHANNEL = 4
DATA_PORT = 1234

# -------------------- WIFI SETUP --------------------
def setup_ap():
    print("Starting Access Point...")

    ap = network.WLAN(network.AP_IF)
    ap.active(True)

    # IMPORTANT FIX: authmode so STA can connect!
    ap.config(
        essid=SSID,
        password=PASSWORD,
        channel=CHANNEL,
        authmode=network.AUTH_WPA_WPA2_PSK
    )

    while not ap.active():
        time.sleep(0.5)

    print("AP ready:", ap.ifconfig())
    return ap

# -------------------- SOCKET SETUP --------------------
def start_socket(port):
    s = socket.socket()
    s.bind(("0.0.0.0", port))
    s.listen(1)
    s.settimeout(1)
    print("Socket listening on port", port)
    return s

# -------------------- CLIENT HANDLER --------------------
def handle_data_client(client):
    """Send JSON repeatedly to client."""  # Example sensor data

    try:
        while True:
            data = sensors.read_all()
            print(data)
            client.send((ujson.dumps(data) + "\n").encode())
            time.sleep(1)
    except Exception as e:
        print("Client disconnected:", e)
    finally:
        client.close()

# -------------------- MAIN LOOP --------------------
def main():
    setup_ap()
    data_socket = start_socket(DATA_PORT)

    while True:
        try:
            client, addr = data_socket.accept()
            print("Client connected:", addr)
            handle_data_client(client)
        except OSError:
            pass  # timeout so loop doesn’t freeze

        time.sleep(0.1)

# -------------------- RUN --------------------
if __name__ == "__main__":
    main()
