import asyncio
import logging
import time
from pathlib import Path
from tkinter import messagebox

import aiofiles
from _socket import gaierror
from anyio import create_task_group
from anyio._backends._asyncio import ExceptionGroup
from async_timeout import timeout

from minecraft_chat import gui
from minecraft_chat.chat_listener import ChatReader
from minecraft_chat.exceptions import NeedAuthLoginError, TokenIsNotValidError
from minecraft_chat.modal_reader import ModalReader
from minecraft_chat.sender import ChatSender
from minecraft_chat.utils import parse_args

watchdog_logger = logging.getLogger("watchdog_logger")
logging.basicConfig(level=logging.INFO)


class ChatMessageApi:
    def __init__(
        self,
        file_path: Path,
        host,
        port,
        username,
        token,
    ):
        self.file_path = file_path
        self.send_host = host
        self.send_port = port
        self.token = token
        self.username = username

        self.status_updates_queue = asyncio.Queue()
        self.watchdog_queue = asyncio.Queue()
        self.saved_messages_queue = asyncio.Queue()
        self.messages_queue = asyncio.Queue()
        self.sending_queue = asyncio.Queue()

    async def handle_connection(self, chat_reader):
        while True:
            try:
                async with create_task_group() as tg:
                    tg.start_soon(self.send_messages)
                    tg.start_soon(self.check_socket_connection)
                    tg.start_soon(self.save_messages)
                    tg.start_soon(self.generate_messages, chat_reader)
                    tg.start_soon(self.watch_for_connection)
            except (ConnectionError, gaierror, ExceptionGroup):
                time.sleep(5)

    async def load_messages(self):
        if not self.file_path.exists():
            return
        async with aiofiles.open(self.file_path, mode="r") as file:
            while True:
                chat_line = await file.readline()
                if not chat_line:
                    break
                await self.messages_queue.put(chat_line.rstrip())

    async def check_socket_connection(self):
        chat_sender = await ChatSender(
            self.send_host,
            self.send_port,
            self.username,
            self.token,
        )
        while True:
            try:
                async with timeout(2):
                    await chat_sender.send_message("")
            except asyncio.TimeoutError:
                continue
            await self.watchdog_queue.put("Connection is alive. Connected to socket")
            await asyncio.sleep(1)

    async def send_messages(self):
        while True:
            chat_sender = await ChatSender(
                self.send_host,
                self.send_port,
                self.username,
                self.token,
            )
            await self.watchdog_queue.put("Connection is alive. Connect to socket")
            if self.token:
                try:
                    serialized_token = await chat_sender.auth()
                except TokenIsNotValidError as exc:
                    messagebox.showerror("token error", str(exc))
                    raise
                await self.watchdog_queue.put("Connection is alive. Authorization done")
                await self.status_updates_queue.put(
                    gui.SendingConnectionStateChanged.ESTABLISHED,
                )
            else:
                serialized_token = await chat_sender.register()
                self.token = serialized_token["account_hash"]
                await self.status_updates_queue.put(
                    gui.SendingConnectionStateChanged.ESTABLISHED,
                )
                await self.watchdog_queue.put("Connection is alive. Registration done")
            nickname = serialized_token["nickname"]
            event = gui.NicknameReceived(nickname)
            await self.status_updates_queue.put(event)

            while True:
                message = await self.sending_queue.get()
                await chat_sender.send_message(message)
                await self.watchdog_queue.put("Connection is alive. Sent message")

    async def generate_messages(self, chat_reader):
        line_reader = chat_reader.read_chat()
        await self.status_updates_queue.put(gui.ReadConnectionStateChanged.INITIATED)

        while True:
            chat_line = await line_reader.__anext__()
            await self.status_updates_queue.put(
                gui.ReadConnectionStateChanged.ESTABLISHED,
            )
            await self.watchdog_queue.put("Connection is alive. New message in chat")
            await self.saved_messages_queue.put(chat_line)
            await self.messages_queue.put(chat_line)

    async def watch_for_connection(self):
        while True:
            try:
                async with timeout(1):
                    log = await self.watchdog_queue.get()
                    watchdog_logger.info(log)
            except asyncio.TimeoutError:
                await self.status_updates_queue.put(
                    gui.ReadConnectionStateChanged.CLOSED,
                )
                await self.status_updates_queue.put(
                    gui.SendingConnectionStateChanged.CLOSED,
                )
                await asyncio.sleep(1)
                await self.status_updates_queue.put(
                    gui.ReadConnectionStateChanged.INITIATED,
                )
                await self.status_updates_queue.put(
                    gui.SendingConnectionStateChanged.INITIATED,
                )

                watchdog_logger.info("1s timeout is elapsed")
                raise ConnectionError

    async def save_messages(self):
        while True:
            async with aiofiles.open(self.file_path, mode="a") as file:
                await file.write(await self.saved_messages_queue.get() + "\n")


async def main():
    ModalReader()
    options = parse_args()
    token = options.token
    username = options.username

    if not token and not username:
        raise NeedAuthLoginError("token and username is None, use any type for auth")

    file_path = options.file_path
    default_file_path = Path(Path.cwd(), "chat_logs.txt")
    file_path = Path(file_path) if file_path else default_file_path

    chat_reader = ChatReader(options.listener_host, options.listener_port)
    chat_message_api = ChatMessageApi(
        file_path,
        options.send_host,
        options.send_port,
        username,
        token,
    )
    async with create_task_group() as tg:
        tg.start_soon(chat_message_api.handle_connection, chat_reader)
        tg.start_soon(chat_message_api.load_messages)
        tg.start_soon(
            gui.draw,
            chat_message_api.messages_queue,
            chat_message_api.sending_queue,
            chat_message_api.status_updates_queue,
        )


def run_main_loop():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except (gui.TkAppClosed, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    run_main_loop()
