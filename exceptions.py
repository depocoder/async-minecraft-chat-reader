class BaseMinecraftChatException(Exception):
    pass


class NeedAuthLoginError(BaseMinecraftChatException):
    pass


class TokenIsNotValidError(BaseMinecraftChatException):
    pass


