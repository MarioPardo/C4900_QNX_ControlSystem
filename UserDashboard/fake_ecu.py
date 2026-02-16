import socket
import json
import time
import random

HOST = "127.0.0.1"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("ECU waiting for dashboard connection...")
conn, addr = server.accept()
print("Dashboard connected:", addr)

speed = 0.0

while True:

    
    speed += random.uniform(-1.0, 1.5)
    if speed < 0:
        speed = 0
    if speed > 100:
        speed = 100

    # simulate wheel sensor failure
    wheel_ok = True
    if int(time.time()) % 12 == 0:
        wheel_ok = False

    packet = {
        "speed": round(speed, 1),
        "wheel_sensor": wheel_ok,
        "warning": "" if wheel_ok else "WHEEL SENSOR TIMEOUT"
    }

    message = json.dumps(packet) + "\n"
    conn.sendall(message.encode())

    time.sleep(0.1)   # 100 ms update
