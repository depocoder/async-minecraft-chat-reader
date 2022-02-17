import datetime
import asyncio
from pathlib import Path

import aiofiles

from utils import parse_chat_listener_args

DEFAULT_FILEPATH = Path(Path.cwd(), 'chat_logs.txt')


async def read_chat(host, port, file_path):
    reader, writer = await asyncio.open_connection(
        host, port)

    while True:
        chat_line_bytes = await reader.readline()
        decoded_chat_line = chat_line_bytes.decode("utf-8").strip()
        now = datetime.datetime.now()
        formatted_time = now.strftime('%H:%M %d.%m.%y')
        formatted_chat_line = f'[{formatted_time}] {decoded_chat_line}'
        async with aiofiles.open(file_path, mode='a') as file:
            await file.write(formatted_chat_line + '\n')
        print(formatted_chat_line)


if __name__ == '__main__':
    options = parse_chat_listener_args()
    host = options.host
    port = options.port
    file_path = options.file_path
    file_path = Path(file_path) if file_path else DEFAULT_FILEPATH
    asyncio.run(read_chat(host, port, file_path))
    