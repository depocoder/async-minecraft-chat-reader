import asyncio
from _socket import gaierror
from tkinter import messagebox
from pathlib import Path

import aiofiles

import gui
from chat_listener import ChatReader
from exceptions import NeedAuthLoginError, TokenIsNotValidError
from sender import ChatSender
from utils import parse_args


async def load_messages(filepath: Path, messages_queue):
    if not filepath.exists():
        return
    async with aiofiles.open(filepath, mode="r") as file:
        while True:
            chat_line = await file.readline()
            if not chat_line:
                break
            await messages_queue.put(chat_line.rstrip())


async def send_messages(sending_queue, status_updates_queue, host, port, username, token):
    while True:
        try:
            chat_sender = await ChatSender(host, port, username, token)
        except (asyncio.exceptions.TimeoutError, gaierror):
            await status_updates_queue.put(gui.SendingConnectionStateChanged.CLOSED)
            await asyncio.sleep(1)
            await status_updates_queue.put(gui.SendingConnectionStateChanged.INITIATED)
            continue
        if token:
            try:
                serialized_token = await chat_sender.auth()
                await status_updates_queue.put(gui.SendingConnectionStateChanged.ESTABLISHED)
            except TokenIsNotValidError as exc:
                messagebox.showerror('token error', str(exc))
                raise
            except (asyncio.exceptions.TimeoutError, gaierror):
                await status_updates_queue.put(gui.SendingConnectionStateChanged.CLOSED)
                await asyncio.sleep(1)
                continue
        else:
            try:
                serialized_token = await chat_sender.register()
                await status_updates_queue.put(gui.SendingConnectionStateChanged.ESTABLISHED)
            except (asyncio.exceptions.TimeoutError, gaierror):
                await status_updates_queue.put(gui.SendingConnectionStateChanged.CLOSED)
                await asyncio.sleep(1)
                continue
        nickname = serialized_token['nickname']
        event = gui.NicknameReceived(nickname)
        await status_updates_queue.put(event)

        while True:
            message = await sending_queue.get()
            try:
                await chat_sender.send_message(message)
            except (asyncio.exceptions.TimeoutError, gaierror):
                await status_updates_queue.put(gui.SendingConnectionStateChanged.CLOSED)
                await asyncio.sleep(1)
                break
        continue


async def generate_messages(messages_queue, chat_reader, filepath: Path, saved_messages_queue, status_updates_queue):
    await load_messages(filepath, messages_queue)
    line_reader = chat_reader.read_chat()
    await status_updates_queue.put(gui.ReadConnectionStateChanged.INITIATED)
    while True:
        try:
            chat_line = await line_reader.__anext__()
        except (asyncio.exceptions.TimeoutError, gaierror):
            await status_updates_queue.put(gui.ReadConnectionStateChanged.CLOSED)
            await asyncio.sleep(1)
            await status_updates_queue.put(gui.ReadConnectionStateChanged.INITIATED)
            line_reader = chat_reader.read_chat()
            continue
        await status_updates_queue.put(gui.ReadConnectionStateChanged.ESTABLISHED)
        await saved_messages_queue.put(chat_line)
        await messages_queue.put(chat_line)


async def save_messages(filepath, queue):
    while True:
        async with aiofiles.open(filepath, mode="a") as file:
            await file.write(await queue.get() + "\n")


if __name__ == '__main__':
    options = parse_args()
    token = options.token
    username = options.username

    if not token and not username:
        raise NeedAuthLoginError("token and username is None, use any type for auth")

    file_path = options.file_path
    default_filepath = Path(Path.cwd(), "chat_logs.txt")
    file_path = Path(file_path) if file_path else default_filepath

    loop = asyncio.get_event_loop()

    messages_queue = asyncio.Queue()
    saved_messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    chat_reader = ChatReader(options.listener_host, options.listener_port)
    asyncio.gather(
        *[generate_messages(messages_queue, chat_reader, file_path, saved_messages_queue, status_updates_queue),
          save_messages(file_path, saved_messages_queue),
          send_messages(sending_queue, status_updates_queue, options.send_host, options.send_port, username, token),
          ]
    )

    try:
        loop.run_until_complete(gui.draw(messages_queue, sending_queue, status_updates_queue))
    except gui.TkAppClosed:
        pass