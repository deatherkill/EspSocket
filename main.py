import socket
import sys
import time
import telebot
from datetime import datetime as dt
import threading
import json

with open('creds.json') as f:
    data = json.load(f)

bot = telebot.TeleBot(data['bot'], threaded=True)
content = ''
server_status = ''
global ip_address
port = data['port']

group_id = data['group_id']
chat_id = data['chat_id']
local = data['local_ip']


def socks():
    while True:
        global content
        try:
            client, addr = s.accept()
            client.settimeout(1)
            content = client.recv(1024).decode()
            # print(content)
            global off_time
            off_time = int(time.time())
        except socket.error as e:
            print('Socket Error:', e)
            client.close()


def timer():
    global prev_state, cur_time, state, server_status
    while True:
        cur_time = int(time.time())
        state = not (cur_time > off_time + delay_time)
        # print(state, prev_state)
        power_check = content == 'Power is OK'
        if state is not prev_state:
            if state and power_check:
                print('On', dt.now().strftime('%Y-%m-%d, %H:%M:%S'))
                timestamp = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
                bot.send_message(chat_id=group_id, text=f'🟢 Power is ON at: {timestamp}', timeout=5)
                server_status = '🟢'
            else:
                print('Off', dt.now().strftime('%Y-%m-%d, %H:%M:%S'))
                timestamp = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
                bot.send_message(chat_id=group_id, text=f'🔴 Power is OFF at: {timestamp}', timeout=5)
                server_status = '🔴'
        prev_state = state


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, f"Bot is working. Status: {server_status}")


@bot.message_handler(commands=['ip'])
def send_welcome(message):
    bot.reply_to(message, text=f'{ip_address}:{port}')


if __name__ == "__main__":

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Socket connection error')
        sys.exit(1)
    s.bind(('0.0.0.0', port))
    s.listen(0)
    hostname = socket.gethostname()

    ip_address = socket.gethostbyname(hostname)
    off_time = 0
    delay_time = 30
    cur_time = time.time()
    state = False
    prev_state = False

    print(f"IP Address: {ip_address}")
    t1 = threading.Thread(target=timer)
    t2 = threading.Thread(target=socks)
    t1.start()
    t2.start()
    bot.infinity_polling()
