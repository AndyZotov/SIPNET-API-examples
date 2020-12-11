#!/usr/bin/env python3
import os, sys
import shutil
import requests
from datetime import datetime, timedelta

# Вычислим дату на вчера, и бкдем использовать её как дату по умолчанию
yesterday = datetime.now() - timedelta(days=1)

# Это переменные для запроса звонков и их записей. см. 
# Описание тут https://newapi.sipnet.ru/apidoc.pdf 

# Определим дефолт на лимит числа скачиваемых файлов. Если это Maxgetfiles=0, то файлы не скачиваются
Maxgetfiles = 8000
Maxgetinit = 8000

# Определим дефолт на дату скачивания записей.
# CurrentDate = '25.11.2020'
CurrentDate = yesterday.strftime('%d.%m.%Y')


# Если есть параметры, перекроем дефолт заданными значениями
if len (sys.argv) == 2: 
   CurrentDate = sys.argv[1]

if len (sys.argv) == 3: 
   CurrentDate = sys.argv[1]
   Maxgetfiles = int(sys.argv[2])
   Maxgetinit = int(sys.argv[2])

# Список дочерних по которым нужны записи. Если дочек нет, указываем один основной аккаунт
managers = {'manage4', 'manage2', 'manage16', 'manage10', 'manage15', 'manage17', 'manage1', 'manage5'}

# Префикс имени главной дирректории, можно пустую строку, или имя аккаунта или любую допустимую для имени дирретории строку
DirPrefix="My_dir_name_prefix_"

# Создадим дирректории в которые положим файлы
try: 
    os.mkdir(DirPrefix + CurrentDate) 
except OSError as error: 
    print(error) 

for path in managers:
    try:
       os.mkdir( DirPrefix + CurrentDate+'/'+path)
    except OSError as error:
       print(error) 
    print ("Успешно создали директорию", path )

# Это URL запроса статистики и его основные параметры
URL = 'https://newapi.sipnet.ru/api.php'

payload = {'operation': 'calls',      # Метод который возвращает статистику звонков и ссылки на записи.
          # 'apikey': '<data>',        # Указать ключ авторизации API. Получить в ВАТС (интерфейс администратора)
          # Использовать одно из двух, или 'apikey': '<data>', или login + password
           'login': '<data>',         # Указать логин аккаунта SIPNET. 
           'password': '<data>',      # Указать пароль аккаунта SIPNET.
           'showchild': '1',          # Если указан 1 то получим данные основного и дочерних аккаунтов.
           'D1': CurrentDate,            # Если не правильная дата, то сегодня
           'D2': CurrentDate,            # Если не правильная дата, то сегодня
           'format': 'json'           # Это формат возвращаемых данных. Нам очень Json понравился
           }

# Напечатаем исходные данные, на всякий случай.
print("===============================================")
print(URL)
print(payload)
print(Maxgetfiles)
print("===============================================")

# Запрашиваем статистику звонков и начинаем разбор полученого.
response= requests.post(URL, data=payload)

if response.status_code == requests.codes.ok:
    dictionary=response.json()
    # нам уже доступна структура данных ответа. Если хотите, напечатайте ее.
    print ("Структура ответа ", dictionary.keys())
    del response
    if dictionary["status"] != 'error':
        if 'calls' in dictionary.keys():
            # нам уже доступна структура данных самого звонка. Если хотите, напечатайте ее.
            print ("Структура звонков ", dictionary["calls"][0].keys())
            print ("Структура [0] ", dictionary["calls"][0])
            # Далее цикл для обхода всех полученых звонков и печати отчета по ним.
            # Статистика обрабатывается от момента запроса к началу дня
            # Для вывода звонков от начала дня к текущему моменту
            # for i in dictionary["calls"]:
            for i in reversed(dictionary["calls"]):
                if 'Phone' in i.keys():
                    print ("======================================================================================================")
                    print (i["CID"], '', i["Account"], '', i['Direction'], '\n', "Дата= " , i["GMT"], "Номер= ", i["Phone"], "АОН= ", i["CLI"], "Длительность= ", i["Duration"])
                else:
                    print ("Странный звонок у него нет номера B")
                if 'URL' in i.keys():
                    # Обнаружен URL файла с записью разговора.
                    print (i["URL"])
                    # Проверяем, не исчерпан ли лимит скачивания файлов
                    if Maxgetfiles>0 and i["Account"] in managers:
                       # Скачаем и сохраним все обнаруженные записи имя сохраненного файла состоит из cid звонка.
                        response = requests.get(i["URL"]+"&r=1", stream=True)
                        if response.status_code == requests.codes.ok:
                            # Тут мы формируем имя файла записи разговора
                            FileName = i["Account"]+"_"+i["GMT"]+"_"+i["CLI"]+"_"+i["Phone"]+"_"+i['Direction']
                            # Определяем тип скаченого файла и выбираем нужное расширение имени файла
                            if response.headers['Content-Type'] == 'audio/mpeg':
                                FileName = FileName+".mp3"
                            else:
                                FileName = FileName+".zip"
                            FileName = FileName.replace('/', '-').replace(':', '-')
                            # Сохраняем скаченый файл с нужным именем.
                            with open(DirPrefix + CurrentDate+'/'+i["Account"]+'/'+FileName, 'wb') as out_file:
                                shutil.copyfileobj(response.raw, out_file)
                            del response
                            Maxgetfiles -= 1
                        else:
                            print ("Запись не скачалась. Получили код ", response.status_code)
                    elif Maxgetfiles == 0:
                        print ("Лимит скачивания исчерпан")
                        break
                else:
                    print ("Нет MP3 записи этого звонка")
            print ("скачали всего ", Maxgetinit - Maxgetfiles)        
        else:
            print ("Результат нормальный, но Нет звонков")
    else:
        print ("Что-то пошло не так. Плохой результат получили ")
        print ("Статус ответа ", dictionary["status"])
        print ("Ошибка ", dictionary["errorCode"], dictionary["errorMessage"])       
else:
    print ("Совсем плохо. Получили код ", response.status_code)

