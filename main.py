import datetime
import asyncio
from pathlib import Path

import configargparse
import aiofiles


DEFAULT_FILEPATH = Path(Path.cwd(), 'chat_logs.txt')


def parse_args() -> configargparse.Namespace:
    parser = configargparse.ArgParser(default_config_files=['.env'])
    parser.add_argument('-p', '--port', type=int, env_var='PORT', required=True, help='port for minecraft server')
    parser.add_argument('-i', '--ip', env_var='IP_ADDRESS', required=True, help='ip for minecraft server')
    parser.add_argument('-f', '--file-path', env_var='FILE_PATH', help='file path for logs')
    return parser.parse_args()


async def read_chat(ip, port, file_path):
    reader, writer = await asyncio.open_connection(
        ip, port)

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
    options = parse_args()
    ip = options.ip
    port = options.port
    file_path = options.file_path
    file_path = Path(file_path) if file_path else DEFAULT_FILEPATH
    asyncio.run(read_chat(ip, port, file_path))
    