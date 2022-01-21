import datetime

import asyncio
import aiofiles


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        'minechat.dvmn.org', 5000)

    while True:
        chat_line_bytes = await reader.readline()
        decoded_chat_line = chat_line_bytes.decode("utf-8").strip()
        now = datetime.datetime.now()
        formatted_time = now.strftime('%H:%M %d.%m.%y')
        formatted_chat_line = f'[{formatted_time}] {decoded_chat_line}'
        async with aiofiles.open('chat_logs.txt', mode='a') as file:
            await file.write(formatted_chat_line + '\n')
        print(formatted_chat_line)


if __name__ == '__main__':
    asyncio.run(tcp_echo_client('Hello World!'))