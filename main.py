import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 8090))
s.listen(0)

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
print(f"Hostname: {hostname}")
print(f"IP Address: {ip_address}")

start_time = 0
delay_time = 10
while True:
    client, addr = s.accept()
    client.settimeout(1)
    while True:
        content = client.recv(1024)
        print(content)
        if len(content) == 0:
            break
        if str(content, 'utf-8') == '\r\n':
            continue
        else:
            print(str(content, 'utf-8'))
            client.send(b'Hello From Python')
    client.close()
