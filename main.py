import asyncio
from tkinter import messagebox
from pathlib import Path

import aiofiles

import gui
from chat_listener import read_chat
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


async def send_messages(sending_queue, host, port, username, token):
    chat_sender = await ChatSender(host, port, username, token)

    if token:
        try:
            await chat_sender.auth()
        except TokenIsNotValidError as exc:
            messagebox.showerror('token error', str(exc))
            raise
    else:
        await chat_sender.register()

    while True:
        message = await sending_queue.get()
        await chat_sender.send_message(message)


async def generate_messages(messages_queue, chat_reader, filepath: Path, saved_messages_queue):
    await load_messages(filepath, messages_queue)
    while True:
        chat_line = await chat_reader.__anext__()
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
    chat_reader = read_chat(options.listener_host, options.listener_port, file_path)
    asyncio.gather(
        *[generate_messages(messages_queue, chat_reader, file_path, saved_messages_queue),
          save_messages(file_path, saved_messages_queue),
          send_messages(sending_queue, options.send_host, options.send_port, username, token),
          ])

    try:
        loop.run_until_complete(gui.draw(messages_queue, sending_queue, status_updates_queue))
    except gui.TkAppClosed:
        pass
