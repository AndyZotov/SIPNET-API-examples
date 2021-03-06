# SIPNET-API-examples
SIPNET это провайдер услуги связи по протоколу SIP. 
Мы понимаем, что программист в штате это роскошь и доступна она не всем, но разобраться с Python, имея примеры, - не сложно даже ребенку. Примеры скриптов для скачивания файлов с записями разговоров, для получения статистики звонков и попыток.
Используйте новый вариант API описанный в документе https://newapi.sipnet.ru/apidoc.pdf.

Задачи, для решения которых есть примеры:

- Скачать записанные звонки (два варианта);
- Записать статистику попыток в файл формата CSV.

Скрипты нужно немного подготовить (\<data\> должно быть заменено на реальные значения.), т.к. данные для авторизации прописываются в самом коде. Для авторизации используется вот этот фрагмент в скриптах.  

```python
payload = {'operation': 'attempts',   # Метод который возвращает статистику попыток вызова.
          # 'apikey': '<data>',        # Указать ключ авторизации API. Получить в ВАТС (интерфейс администратора)
          # Использовать одно из двух, или 'apikey': '<data>', или login + password
           'login': '<data>',         # Указать логин аккаунта SIPNET. 
           'password': '<data>',      # Указать пароль аккаунта SIPNET.
           'showchild': '0',          # Если указан 1 то получим данные основного и дочерних аккаунтов.
           'D1': CurrentDate,        # Если не правильная дата, то сегодня
           'D2': CurrentDate,        # Если не правильная дата, то сегодня
           'format': 'json'           # Это формат возвращаемых данных. Нам очень Json понравился
           }
```

Скрипты принимают один или два параметра из команды запуска. 
Пример:

```bash
user@desktop:~/Python/SIPNET-API-examples$ ./newAPI_getMP3-2-folders.py 10.12.2020 1000
```

Первый параметр это дата на которую нужно просмотреть статистику (формат даты ('%d.%m.%Y') ) например 10.12.2020. 

Второй параметр, это число скачиваемых файлов например 1000. 

Оба параметра можно не указывать, тогда скрипт использует значения по умолчанию, это дата на предыдущий день и максимальное число скачиваемых файлов равно 8000. Вот в этом фрагменте кода это определяется.

```python
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

```

