import datetime

from _socket import gaierror
from retry import retry

from minecraft_chat.utils import get_logger, managed_open_connection

logger = get_logger()


class ChatReader:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @retry(gaierror, tries=3, delay=10, jitter=2, logger=logger)
    async def read_chat(self):
        async with (managed_open_connection(self.host, self.port)) as (reader, writer):
            while True:
                chat_line_bytes = await reader.readline()
                decoded_chat_line = chat_line_bytes.decode("utf-8").strip()
                now = datetime.datetime.now()
                formatted_time = now.strftime("%H:%M %d.%m.%y")
                formatted_chat_line = f"[{formatted_time}] {decoded_chat_line}"
                yield formatted_chat_line
