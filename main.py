import socket
import time
import telebot
from datetime import datetime as dt
import threading

bot = telebot.TeleBot("5841428040:AAGRVyc-EVDY1cFPHv-NfzQRATzyDJWaE3k", threaded=True)
chat_id = 648624553

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 8090))
s.listen(0)

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
print(f"Hostname: {hostname}")
print(f"IP Address: {ip_address}")

off_time = 0
delay_time = 4
cur_time = time.time()
state = False
prev_state = False


def socks():
    while True:
        try:
            client, addr = s.accept()
            client.settimeout(1)
            # content = client.recv(1024).decode()
            # print(content)
            global off_time
            off_time = int(time.time())
            # print(off_time)
        except:
            print('Not connected')
            client.close()


def timer():
    # print(off_time)
    global prev_state
    while True:
        cur_time = int(time.time())
        state = not (cur_time > off_time + delay_time)
        # print(state, prev_state)
        if state is not prev_state:
            if state:
                print('On', dt.now().strftime('%Y-%m-%d, %H:%M:%S'))
                timestamp = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
                bot.send_message(chat_id=chat_id, text=f'🟢Power is ON at: {timestamp}', timeout=5)
            else:
                print('Off', dt.now().strftime('%Y-%m-%d, %H:%M:%S'))
                timestamp = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
                bot.send_message(chat_id=chat_id, text=f'🟠Power is OFF at: {timestamp}', timeout=5)
        prev_state = state


if __name__ == "__main__":
    t1 = threading.Thread(target=timer)
    t2 = threading.Thread(target=socks)
    t1.start()
    t2.start()
# while True:
#     # client, addr = s.accept()
#     try:
#         client, addr = s.accept()
#         client.settimeout(1)
#         content = client.recv(1024)
#         print(content)
#     except:
#         print('Not connected')

# while True:
#     content = s.recv(1024)
#     if len(content) == 0:
#         break
#     if str(content, 'utf-8') == '\r\n':
#         continue
#     else:
#         off_time = int(time.time())
#         state = True
#
# if int(time.time()) > off_time + delay_time:
#     state = False
#
# if state:
#     print('On', dt.now().strftime('%Y-%m-%d, %H:%M:%S'))
# else:
#     print('Off', dt.now().strftime('%Y-%m-%d, %H:%M:%S'))
# client.close()

# start_time = int(time.time())
# while True:
