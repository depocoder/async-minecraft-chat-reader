import asyncio
from pathlib import Path

import gui
from chat_listener import read_chat
from utils import parse_chat_listener_args


async def generate_msgs(queue, chat_reader):
    while True:
        chat_line = await chat_reader.__anext__()
        await messages_queue.put(chat_line)


if __name__ == '__main__':
    reader_options = parse_chat_listener_args()
    file_path = reader_options.file_path
    default_filepath = Path(Path.cwd(), "chat_logs.txt")
    file_path = Path(file_path) if file_path else default_filepath

    loop = asyncio.get_event_loop()

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    chat_reader = read_chat(reader_options.host, reader_options.port, file_path)
    asyncio.gather(*[generate_msgs(messages_queue, chat_reader)])
    try:
        loop.run_until_complete(gui.draw(messages_queue, sending_queue, status_updates_queue))
    except gui.TkAppClosed:
        pass
