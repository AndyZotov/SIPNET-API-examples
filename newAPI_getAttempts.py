#!/usr/bin/env python3
import sys
import requests
import csv
from datetime import datetime, timedelta

# Вычислим дату на вчера, и бкдем использовать её как дату по умолчанию
yesterday = datetime.now() - timedelta(days=1)

# Это переменные для запроса звонков и их записей. см. 
# Описание тут https://newapi.sipnet.ru/apidoc.pdf 

# Определим дефолт на лимит числа скачиваемых файлов. Если это Maxgetfiles=0, то файлы не скачиваются
Maxgetfiles = 8000
Maxgetinit = 8000

# Определим дефолт на дату скачивания записей.
# ListDate = '25.11.2020'
ListDate = yesterday.strftime('%d.%m.%Y')


# Если есть параметры, перекроем дефолт заданными значениями
if len (sys.argv) == 2: 
   ListDate = sys.argv[1]

if len (sys.argv) == 3: 
   ListDate = sys.argv[1]
   Maxgetfiles = int(sys.argv[2])
   Maxgetinit = int(sys.argv[2])

# Это URL запроса статистики и его основные параметры
URL = 'https://newapi.sipnet.ru/api.php'

payload = {'operation': 'attempts',   # Метод который возвращает статистику попыток вызова.
          # 'apikey': '<data>',        # Указать ключ авторизации API. Получить в ВАТС (интерфейс администратора)
          # Использовать одно из двух, или 'apikey': '<data>', или login + password
           'login': '<data>',         # Указать логин аккаунта SIPNET. 
           'password': '<data>',      # Указать пароль аккаунта SIPNET.
           'showchild': '0',          # Если указан 1 то получим данные основного и дочерних аккаунтов.
           'D1': ListDate,        # Если не правильная дата, то сегодня
           'D2': ListDate,        # Если не правильная дата, то сегодня
           'format': 'json'           # Это формат возвращаемых данных. Нам очень Json понравился
           }

# Напечатаем исходные данные, на всякий случай.
print("===============================================")
print(URL)
print(payload)
print(Maxgetfiles)
print("===============================================")

# Запрашиваем статистику попыток и начинаем разбор полученого.
response= requests.post(URL, data=payload)

if response.status_code == requests.codes.ok:
    dictionary=response.json()
    # нам уже доступна структура данных ответа. Если хотите, напечатайте ее.
    print ("Структура ответа ", dictionary.keys())
    del response
    if dictionary["status"] != 'error':
        if 'attempts' in dictionary.keys():
            employee_data = dictionary["attempts"]
            if len(employee_data) != 0:
                # нам уже доступна структура данных попытки. Если хотите, напечатайте ее.
                print ("Структура попыток ", employee_data[0].keys())
                print ("Структура [1] ", employee_data[0])

                # Открываем файл в который записывать данные
                data_file = open('data_file.csv', 'w')
                # Создаем csv writer object 
                csv_writer = csv.writer(data_file) 
                # Счётчик числа записей
                # Для вставки заголовка в первой строке CSV файла
                count = 0
                for emp in employee_data: 
                    if count == 0: 
                        # Запишем заголовок для CSV файла
                        header = emp.keys()
                        csv_writer.writerow(header)
                        count += 1
                    # Запишем данные в CSV файл
                    csv_writer.writerow(emp.values()) 
                    # Запись закончена CSV файл закрываем
                    data_file.close() 
                # Далее цикл для обхода всех полученых попыток и печати отчета по ним.
                # Статистика обрабатывается от момента запроса к началу дня
                # Для вывода попыток от начала дня к текущему моменту
                # for i in dictionary["attempts"]:
                for emp in reversed(employee_data):
                    if 'Phone' in emp.keys():
                       print ("======================================================================================================")
                       print (emp["GMT"], '', emp["Account"], '\n', "Дата= " , emp["GMT"], "Номер= ", emp["Phone"], "АОН= ", emp["CLI"], "Q.850 Cause Codes= ", emp["ISDNCode"], ' ', emp["ISDNDescr"])
                    else:
                        print ("Странно у него нет номера B")
            else:
                 print ("Результат нормальный, но Нет попыток")
        else:
            print ("Результат нормальный, но Нет попыток")
    else:
        print ("Что-то пошло не так. Плохой результат получили ")
        print ("Статус ответа ", dictionary["status"])
        print ("Ошибка ", dictionary["errorCode"], dictionary["errorMessage"])       
else:
    print ("Совсем плохо. Получили код ", response.status_code)
