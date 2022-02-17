import asyncio
import json
import logging

from exceptions import NeedAuthLoginError, TokenIsNotValidError
from utils import parse_sender_args


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def read_line(reader) -> str:
    chat_line_bytes = await reader.readline()
    return chat_line_bytes.decode("utf-8").strip()


async def write_bytes(writer, data: str) -> None:
    sanitized_data = data.replace('\\', '\\\\')
    encoded_data = f'{sanitized_data}\n'.encode()
    writer.write(encoded_data)
    await writer.drain()


async def register(reader, writer, username: str):
    logger.info(await read_line(reader))
    await write_bytes(writer, '')
    logger.info(await read_line(reader))
    await write_bytes(writer, username)
    serialized_token = json.loads(await read_line(reader))
    with open('token.json', 'w') as token_file:
        json.dump(serialized_token, token_file)
        logger.info('Your token written in token.json')
    logger.info(await read_line(reader))


async def auth(reader, writer, token: str):
    logger.info(await read_line(reader))

    await write_bytes(writer, token)

    serialized_token = json.loads(await read_line(reader))
    if serialized_token is None:
        raise TokenIsNotValidError('Your token was not accepted from server')
    logger.info(serialized_token)
    logger.info(await read_line(reader))


async def send_message(host: str, port: int, message: str, username: str, token: str):
    reader, writer = await asyncio.open_connection(
        host, port)

    if token:
        await auth(reader, writer, token)
    else:
        await register(reader, writer, username)

    message += '\n'
    await write_bytes(writer, message)

if __name__ == '__main__':
    options = parse_sender_args()
    host = options.host
    port = options.port
    token = options.token
    username = options.username

    if not token and not username:
        raise NeedAuthLoginError('token and username is None, use any type for auth')
    asyncio.run(send_message(host, port, 'Hello World!', username, token))
