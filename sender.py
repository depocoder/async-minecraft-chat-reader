import asyncio
import logging

from exceptions import NeedAuthLoginError, TokenIsNotValidError
from utils import parse_args


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def read_line(reader) -> str:
    chat_line_bytes = await reader.readline()
    return chat_line_bytes.decode("utf-8").strip()


async def write_bytes(writer, data: str) -> None:
    encoded_data = f'{data}\n'.encode()
    writer.write(encoded_data)
    await writer.drain()


async def auth(reader, writer, username: str, token: str):
    read_greeting = await read_line(reader)
    logger.info(read_greeting)

    token = token if token else ''
    await write_bytes(writer, token)

    read_auth_greetings = await read_line(reader)
    if read_auth_greetings == 'null':
        raise TokenIsNotValidError('Your token was not accepted from server')
    logger.info(read_auth_greetings)
    if token:
        return

    await write_bytes(writer, username)
    logger.info(await read_line(reader))


async def send_message(host: str, port: int, message: str, username: str, token: str):
    reader, writer = await asyncio.open_connection(
        host, port)

    await auth(reader, writer, username, token)

    chat_greeting = await read_line(reader)
    logger.info(chat_greeting)
    message += '\n'
    await write_bytes(writer, message)

if __name__ == '__main__':
    options = parse_args()
    host = options.host
    port = options.port
    token = options.token
    username = options.username

    if not token and not username:
        raise NeedAuthLoginError('token and username is None, use any type for auth')
    asyncio.run(send_message(host, port, 'Hello World!', username, token))
