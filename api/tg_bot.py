import requests
from loguru import logger

from config import TGBOT_TOKEN


class TGBot:
    URL_SEND_MESSAGE = \
        'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'
    TGBOT_TOKEN = TGBOT_TOKEN

    @classmethod
    def send_message(cls, user_id: str, message: str) -> None:
        uri = cls.URL_SEND_MESSAGE.format(cls.TGBOT_TOKEN, user_id, message)
        with requests.post(uri) as _:
            pass
        logger.debug(f'Send message to user # {user_id}: {message[:10]}...')
