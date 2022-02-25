import asyncio
import logging
from _socket import gaierror
from tkinter import messagebox
from pathlib import Path

import aiofiles
from async_timeout import timeout

import gui
from chat_listener import ChatReader
from exceptions import NeedAuthLoginError, TokenIsNotValidError
from sender import ChatSender
from utils import parse_args

watchdog_logger = logging.getLogger('watchdog_logger')
logging.basicConfig(level=logging.INFO)


class ChatMessageApi:
    def __init__(self, file_path: Path, host, port, username, token, ):
        self.file_path = file_path
        self.send_host = host
        self.send_port = port
        self.token = token
        self.username = username

        self.messages_queue = asyncio.Queue()
        self.status_updates_queue = asyncio.Queue()
        self.watchdog_queue = asyncio.Queue()
        self.saved_messages_queue = asyncio.Queue()
        self.sending_queue = asyncio.Queue()

    async def load_messages(self):
        if not self.file_path.exists():
            return
        async with aiofiles.open(self.file_path, mode="r") as file:
            while True:
                chat_line = await file.readline()
                if not chat_line:
                    break
                await self.messages_queue.put(chat_line.rstrip())

    async def send_messages(self):
        while True:
            try:
                chat_sender = await ChatSender(self.send_host, self.send_port, self.username, self.token)
            except (asyncio.exceptions.TimeoutError, gaierror):
                await self.watchdog_queue.put('Connection is not alive. Can\'t connect to socket')
                await self.status_updates_queue.put(gui.SendingConnectionStateChanged.CLOSED)
                await asyncio.sleep(1)
                await self.status_updates_queue.put(gui.SendingConnectionStateChanged.INITIATED)
                continue
            await self.watchdog_queue.put('Connection is alive. Connect to socket')
            if self.token:
                try:
                    serialized_token = await chat_sender.auth()
                    await self.watchdog_queue.put('Connection is alive. Authorization done')
                    await self.status_updates_queue.put(gui.SendingConnectionStateChanged.ESTABLISHED)
                except TokenIsNotValidError as exc:
                    messagebox.showerror('token error', str(exc))
                    raise
                except (asyncio.exceptions.TimeoutError, gaierror):
                    await self.watchdog_queue.put('Connection is not alive. Authorization is not done')
                    await self.status_updates_queue.put(gui.SendingConnectionStateChanged.CLOSED)
                    await asyncio.sleep(1)
                    continue
            else:
                try:
                    serialized_token = await chat_sender.register()
                    self.token = serialized_token['account_hash']
                    await self.status_updates_queue.put(gui.SendingConnectionStateChanged.ESTABLISHED)
                    await self.watchdog_queue.put('Connection is alive. Registration done')
                except (asyncio.exceptions.TimeoutError, gaierror):
                    await self.watchdog_queue.put('Connection is not alive. Registration is not done')
                    await self.status_updates_queue.put(gui.SendingConnectionStateChanged.CLOSED)
                    await asyncio.sleep(1)
                    continue
            nickname = serialized_token['nickname']
            event = gui.NicknameReceived(nickname)
            await self.status_updates_queue.put(event)

            while True:
                message = await self.sending_queue.get()
                try:
                    await chat_sender.send_message(message)
                    await self.watchdog_queue.put('Connection is alive. Sent message')
                except (asyncio.exceptions.TimeoutError, gaierror):
                    await self.watchdog_queue.put('Connection is not alive. Can not send message')
                    await self.status_updates_queue.put(gui.SendingConnectionStateChanged.CLOSED)
                    await asyncio.sleep(1)
                    break
            continue

    async def generate_messages(self, chat_reader):
        await self.load_messages()
        line_reader = chat_reader.read_chat()
        await self.status_updates_queue.put(gui.ReadConnectionStateChanged.INITIATED)
        while True:
            try:
                chat_line = await line_reader.__anext__()
            except (asyncio.exceptions.TimeoutError, gaierror):
                await self.watchdog_queue.put('Connection is not alive. Can not read message in chat')
                await self.status_updates_queue.put(gui.ReadConnectionStateChanged.CLOSED)
                await asyncio.sleep(1)
                await self.status_updates_queue.put(gui.ReadConnectionStateChanged.INITIATED)
                line_reader = chat_reader.read_chat()
                continue
            await self.status_updates_queue.put(gui.ReadConnectionStateChanged.ESTABLISHED)
            await self.watchdog_queue.put('Connection is alive. New message in chat')
            await self.saved_messages_queue.put(chat_line)
            await self.messages_queue.put(chat_line)

    async def watch_for_connection(self):
        while True:
            try:
                async with timeout(1) as cm:
                    log = await self.watchdog_queue.get()
                    watchdog_logger.info(log)
            except asyncio.TimeoutError:
                watchdog_logger.info('1s timeout is elapsed')

    async def save_messages(self):
        while True:
            async with aiofiles.open(self.file_path, mode="a") as file:
                await file.write(await self.messages_queue.get() + "\n")


if __name__ == '__main__':
    options = parse_args()
    token = options.token
    username = options.username

    if not token and not username:
        raise NeedAuthLoginError("token and username is None, use any type for auth")

    file_path = options.file_path
    default_file_path = Path(Path.cwd(), "chat_logs.txt")
    file_path = Path(file_path) if file_path else default_file_path

    loop = asyncio.get_event_loop()

    chat_reader = ChatReader(options.listener_host, options.listener_port)
    chat_message_api = ChatMessageApi(file_path, options.send_host, options.send_port, username, token, )
    asyncio.gather(
        *[chat_message_api.generate_messages(chat_reader),
          chat_message_api.save_messages(),
          chat_message_api.watch_for_connection(),
          chat_message_api.send_messages(),
          ]
    )

    loop.run_until_complete(gui.draw(chat_message_api.messages_queue, chat_message_api.sending_queue,
                                     chat_message_api.status_updates_queue))
