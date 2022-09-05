import asyncio
import json
from _socket import gaierror
from typing import Union

from asyncinit import asyncinit
from retry import retry

from exceptions import NeedAuthLoginError, TokenIsNotValidError
from utils import get_logger


logger = get_logger()


@asyncinit
class ChatSender:
    async def __init__(
        self, host, port, username: Union[str, None], token: Union[str, None]
    ):
        self.reader, self.writer = await asyncio.open_connection(host, port)
        if not token and not username:
            raise NeedAuthLoginError(
                "token and username is None, use any type for auth"
            )

        self.username = username
        self.token = token

    async def read_line(self) -> str:
        chat_line_bytes = await asyncio.wait_for(self.reader.readline(), timeout=10)
        return chat_line_bytes.decode("utf-8").strip()

    async def write_bytes(self, data: str) -> None:
        sanitized_data = data.replace("\\", "\\\\")
        encoded_data = f"{sanitized_data}\n".encode()
        self.writer.write(encoded_data)
        await self.writer.drain()

    async def register(self):
        logger.info(await self.read_line())
        await self.write_bytes("")
        logger.info(await self.read_line())
        await self.write_bytes(self.username)
        serialized_token = json.loads(await self.read_line())
        with open("token.json", "w") as token_file:
            json.dump(serialized_token, token_file)
            logger.info("Your token written in token.json")
        logger.info(await self.read_line())
        return serialized_token

    async def auth(self):
        logger.info(await self.read_line())

        await self.write_bytes(self.token)

        serialized_token = json.loads(await self.read_line())
        if serialized_token is None:
            raise TokenIsNotValidError("Your token was not accepted from server")
        logger.info(serialized_token)
        logger.info(await self.read_line())
        return serialized_token

    @retry(gaierror, tries=3, delay=10, jitter=2, logger=logger)
    async def send_message(self, message: str):

        message += "\n"
        await self.write_bytes(message)
        await self.read_line()
        logger.info("Your message successfully sent")
