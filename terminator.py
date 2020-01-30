#!/usr/bin/env python3

import requests  
import datetime

class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            #last_update = get_result[len(get_result)]
            last_update = None

        return last_update

greet_bot = BotHandler('791233601:AAGpNYMAnohLMAYBMJpaByXPtXPWCqt5Bow')
now = datetime.datetime.now()

def main():  
    new_offset = None
    today = now.day
    hour = now.hour

    while True:
        greet_bot.get_updates(new_offset)

        last_update = greet_bot.get_last_update()
        if last_update is None:
            continue

        if last_update != None:
            last_update_id = last_update['update_id']
            last_chat_text = last_update['message']['text']
            last_chat_id = last_update['message']['chat']['id']
            if 'title' in last_update['message']['chat']:
                last_chat_name = last_update['message']['chat']['title']
            
                # Управляющее слово /заявки
                if last_chat_text[0:7].lower() == '/заявка':
                    strings = last_chat_text.lower().split('\n')
                    for string in strings:
                        if '-' in string:
                            fields = string.split('-', maxsplit=1)
                            if fields[0].isnumeric() and len(fields) == 2 and len(fields[1]) > 0:
                                f_requests = open('requests.txt', 'a+')
                                for field in fields:
                                    f_requests.write(field.strip() + ';')
                                f_requests.write('\n')
                                f_requests.close()
                                greet_bot.send_message(last_chat_id, 'Заявка "{}" добавлена в список.'.format(string))
                            else:
                                greet_bot.send_message(last_chat_id, 'Я не понял заявку: "{}". Повторите ее правильно пожалуйста.'.format(string))

                # Управляющее слово /покажи
                elif last_chat_text[0:7].lower() == '/покажи':
                    f_requests = open('requests.txt', 'r')
                    strings = f_requests.read()
                    f_requests.close()
                    greet_bot.send_message(last_chat_id, strings)

                # Управляющее слово /<номер скважины>
                elif last_chat_text[0] == '/' and last_chat_text.split('\n')[0][1:].strip().isnumeric() and len(last_chat_text.split('\n')) == 2:
                    f_requests = open('requests.txt', 'r')
                    strings = f_requests.read().split('\n')
                    f_requests.close()
                    skv = last_chat_text.split('\n')[0][1:].strip()
                    for string in strings:
                        if string.split(';')[0] == skv:
                            strings.remove(string)
                            f_archive = open('archive.txt', 'a+')
                            f_archive.write(skv + ';' + datetime.datetime.now().strftime('%M:%S:%H %d/%m/%Y') + ';' + last_chat_text.split('\n')[1] + ';\n')
                            f_archive.close()
                            greet_bot.send_message(last_chat_id, 'Заявка по скважине {} выполнена.'.format(skv))
                            break
                    f_requests = open('requests.txt', 'w')
                    f_requests.write('\n'.join(strings) + '\n')
                    f_requests.close()

                # Управляющее слово /покажи статистику

                # Управляющее слово /покажи статистику с <дд><мм><гг> по <дд><мм><гг> 

            elif 'first_name' in last_update['message']['chat']:
                last_chat_name = last_update['message']['chat']['first_name']
                greet_bot.send_message(last_chat_id, 'Где Джон Конор? Скажи мне, {}!'.format(last_chat_name))

            new_offset = last_update_id + 1

if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()

