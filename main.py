import socket
import time
import telebot
from datetime import datetime as dt
import threading
import json
import os
from sys import platform
from os.path import exists

LINUX = platform == 'linux' or platform == 'linux2'
WIN = platform == 'win32'
credits_path = ''
if LINUX:
    credits_path = '/home/python-server/credits.json'
elif WIN:
    credits_path = 'credits.json'
with open(credits_path) as f:
    data = json.load(f)

log_file_path = ''
if LINUX:
    log_file_path = '/home/python-server/log.txt'
elif WIN:
    log_file_path = 'log.txt'

file_exists = exists(log_file_path)
if file_exists:
    f = open("log.txt", "w")
    f.close()

bot = telebot.TeleBot(data['bot'], threaded=True)
content = ''
server_status = '🔴'

port = data['port']

group_id = data['group_id']
chat_id = data['chat_id']
local = data['local_ip']

global ip_address


def write_to_log(log_data: str):
    with open(log_file_path, 'a') as log:
        log.write(log_data)


def socks():
    while True:
        global content, client
        try:
            global off_time
            client, addr = s.accept()
            client.settimeout(1)
            content = client.recv(1024).decode()
            # print(content)
            temp_time = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
            write_to_log(f'Received from ESP: {content}, at: {temp_time} \n')
            if content == 'Power is OK':
                off_time = int(time.time())
        except socket.error as e:
            print('Socket Error:', e)
            temp_time = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
            write_to_log(f'Socket error connection at: {temp_time} \n')
            client.close()
            os.system("sudo systemctl restart esp")
        time.sleep(0.1)


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
                write_to_log(f'Change status: Power is ON at: {timestamp} \n')
            elif not state:
                print('Off', dt.now().strftime('%Y-%m-%d, %H:%M:%S'))
                timestamp = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
                bot.send_message(chat_id=group_id, text=f'🔴 Power is OFF at: {timestamp}', timeout=5)
                server_status = '🔴'
                write_to_log(f'Change status: Power is OFF at: {timestamp},'
                             f' Application time: {cur_time},'
                             f' Delay time: {off_time + delay_time} \n')
        prev_state = state
        time.sleep(0.1)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, f"Bot is working. Status: {server_status}")


@bot.message_handler(commands=['ip'])
def send_welcome(message):
    bot.reply_to(message, text=f'{ip_address}:{port}')


@bot.message_handler(commands=['log'])
def send_welcome(message):
    with open(log_file_path, 'r') as log:
        msg = log.read()
    bot.reply_to(message, text=f'Log file opened: {msg}')


@bot.message_handler(commands=['clearlog'])
def send_welcome(message):
    open(log_file_path, 'w').close()
    bot.reply_to(message, text=f'Log file erased')


if __name__ == "__main__":
    global s
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Socket connection error')
        os.system("sudo systemctl restart esp")
    if LINUX:
        s.bind(('185.25.118.34', port))
    elif WIN:
        s.bind(('0.0.0.0', port))
    s.listen(0)
    hostname = socket.gethostname()
    if LINUX:
        ip_address = socket.gethostbyname(local)
    elif WIN:
        ip_address = socket.gethostbyname(hostname)
    off_time = 0
    delay_time = 30
    cur_time = time.time()
    state = False
    prev_state = False
    temp_time = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
    write_to_log(f'Application started at: {temp_time} \n')
    print(f"IP Address: {ip_address}")

    t1 = threading.Thread(target=timer)
    t2 = threading.Thread(target=socks)
    t1.start()
    t2.start()
    bot.infinity_polling()
