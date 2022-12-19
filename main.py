import socket
import time
import telebot
from datetime import datetime as dt
import threading
import json
import os
from sys import platform
from os.path import exists
from io import BytesIO
import sys

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
server_status = 'Undefined'

port = data['port']

group_id = data['group_id']
chat_id = data['chat_id']
local = data['local_ip']


def write_to_log(log_data: str):
    with open(log_file_path, 'a') as log:
        log.write(log_data)


def socks():
    while True:
        global content, client
        content = ''
        try:
            global off_time
            client, addr = s.accept()
            try:
                content = client.recv(1024).decode('utf-8')
            except UnicodeDecodeError:
                content = ''
            # print(content)
            temp_time = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
            if dt.now().minute % 10 == 0 and (0 < dt.now().second < 10):
                write_to_log(f'Received from ESP: {content}, at: {temp_time} \n')
            # if content == 'Power is OK':
            off_time = int(time.time())
        except OSError as e:
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
        power_check = content == 'Power is OK'
        # print(f's:{state}, ps:{prev_state}, pc:{power_check}, ot:{off_time}, c:{content}')
        if state != prev_state:
            if state and power_check and server_status != '🟢':
                # print('On', dt.now().strftime('%Y-%m-%d, %H:%M:%S'))
                timestamp = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
                send_message(chat_id=group_id, text=f'🟢 Power is ON at: {timestamp}', timeout=5)
                server_status = '🟢'
                write_to_log(
                    f't: {timestamp},'
                    f's:{state},'
                    f'p_s:{prev_state},'
                    f'p_c:{power_check},'
                    f'o_t:{off_time},'
                    f'c:{content}\n')
            elif not power_check and (server_status == '🟢' or server_status == 'Undefined'):
                # print('Off', dt.now().strftime('%Y-%m-%d, %H:%M:%S'))
                timestamp = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
                send_message(chat_id=group_id, text=f'🔴 Power is OFF at: {timestamp}', timeout=5)
                server_status = '🔴'
                write_to_log(f't: {timestamp},'
                             f' s:{state},'
                             f' p_s:{prev_state},'
                             f'p_c:{power_check},'
                             f' o_t:{off_time},'
                             f' c:{content}\n')
        prev_state = state
        time.sleep(0.1)


def send_message(chat_id, text, timeout=10):
    try:
        bot.send_message(chat_id=chat_id, text=text, timeout=timeout)
    except Exception as e:
        write_to_log(f'Telegram sending error: {e}')
        return


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.reply_to(message, f"Bot is working. Status: {server_status}")
    except Exception as e:
        write_to_log(f'Telegram sending error: {e}')
        return


@bot.message_handler(commands=['ip'])
def send_welcome(message):
    try:
        bot.reply_to(message, text=f'{ip_address}:{port}')
    except Exception as e:
        write_to_log(f'Telegram sending error: {e}')
        return


@bot.message_handler(commands=['log'])
def send_welcome(message):
    with open(log_file_path, 'rb') as log:
        msg = log.read()
        file_obj = BytesIO(msg)
        file_obj.name = 'log.txt'
        try:
            bot.reply_to(message, text=f'Log file generated')
            bot.send_document(chat_id, document=file_obj)
        except Exception as e:
            write_to_log(f'Telegram sending error: {e}')
            return


@bot.message_handler(commands=['clearlog'])
def send_welcome(message):
    open(log_file_path, 'w').close()
    try:
        bot.reply_to(message, text=f'Log file erased')
    except Exception as e:
        write_to_log(f'Telegram sending error: {e}')
        return


@bot.message_handler(commands=['state'])
def send_welcome(message):
    timestamp = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
    write_to_log(f't: {timestamp}, s:{state}, p_s:{prev_state}, o_t:{off_time}, c:{content}\n')
    try:
        bot.reply_to(message,
                     text=f't: {timestamp},'
                          f's:{state},'
                          f'p_s:{prev_state},'
                          f'o_t:{off_time},'
                          f' c:{content},'
                          f' s_s:{server_status}\n')
    except Exception as telegram_exception:
        write_to_log(f'Telegram sending error: {telegram_exception}')
        return


@bot.message_handler(commands=['restart'])
def send_welcome(message):
    try:
        bot.reply_to(message, text=f'Restarting process')
    except Exception as e:
        write_to_log(f'Telegram sending error: {e}')
        return
    os.popen("sudo systemctl restart esp")


if __name__ == "__main__":
    global s, ip_address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except OSError as e:
        print('Socket connection error')
        temp_time = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
        write_to_log(f'Socket error connection at: {temp_time}, type={s.proto} \n')
        os.system("sudo systemctl restart esp")
    if LINUX:
        s.bind(('', port))
    elif WIN:
        s.bind(('0.0.0.0', port))
    s.listen(0)
    hostname = socket.gethostname()
    if LINUX:
        ip_address = socket.gethostbyname(local)
    elif WIN:
        ip_address = socket.gethostbyname(hostname)
    delay_time = 5
    cur_time = time.time()
    state = False
    prev_state = True
    off_time = cur_time
    temp_time = dt.now().strftime('%Y-%m-%d, %H:%M:%S')
    write_to_log(f'Application started at: {temp_time} \n')
    print(f"IP Address: {ip_address}")
    send_message(chat_id=chat_id, text=f'Bot started successfully', timeout=5)
    t1 = threading.Thread(target=timer)
    t2 = threading.Thread(target=socks)
    t2.start()
    t1.start()
    bot.infinity_polling()
