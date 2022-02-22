# async-minecraft-chat-reader
 
Взаимодействие с чатом minecraft     

## Возможности
- Регистрация (После регистрации токен для авторизации кладется в корень с названием token.json)
- Авторизация по токену
- Отправка сообщения
- Чтение чата и хранение в файле


## Подготовка к запуску(Linux)    
Установить [Python 3+](https://www.python.org/downloads/)    

```shell
sudo apt-get install python3-tk
```


```shell
pip3 install -r requirements.txt
```

### Переменные окружения:
Хранить переменные окружения в корне проета в файле .env

#### Для чтения чата:
    FILE_PATH - Путь где будет храниться файл с логами чата

#### Для отправки сообщения
    TOKEN - Токен пользователя
    USERNAME - Имя пользователя(используется если нет токена)

Для запуска чтения чата обязательные аргументы host, port.

Для запуска отправки сообщения обязательные аргументы host, port, token или username 

## Запуск чтения 

```
python3 chat_listener.py 
```
## Запуск отправки сообщения 

```
python3 sender.py -u depocode -sh minechat.ds.org -sp 5021 -m hello world!
```
