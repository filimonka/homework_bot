"""Бот Telegram проверяющий статус проверки проекта Я.Practicum."""


from http import HTTPStatus
import logging
import os
import sys
import time
import requests

import telegram

from dotenv import load_dotenv

import exceptions

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(funcName)s, %(lineno)s: %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправка сообщения о статусе работы или ошибке."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Сообщение отправлено.')
    except exceptions.MessageError as error:
        logger.error('Сообщение не отправлено', error, exc_info=True)


def get_api_answer(current_timestamp):
    """Получение ответа сервера."""
    timestamp = current_timestamp or int(time.time())
    api_answer = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params={'from_date': timestamp}
    )
    if api_answer.status_code == HTTPStatus.OK:
        return api_answer.json()
    else:
        logger.error(api_answer.status_code, exc_info=True)
        raise exceptions.InvalidResponceStatus(api_answer)


def check_response(response):
    """Проверка полей ответа сервера."""
    if isinstance(response, dict) and isinstance(response['homeworks'], list):
        return response['homeworks']
    else:
        logger.error('response не соответствует ожиданиям')
        raise TypeError()


def parse_status(homework):
    """Получение данных о статусе работы."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except exceptions.DictKeyAbsence as error:
        logger.error(
            'В homework отсутствует необходимый ключ',
            error,
            exc_info=True
        )
        raise KeyError()
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except exceptions.DictKeyAbsence as error:
        logger.error('Неизвестный статус', error, exc_info=True)
        raise KeyError()


def check_tokens():
    """Проверка доступности всех необходимых токенов."""
    tokens = (
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    )
    if all(tokens):
        return True
    else:
        for token in tokens:
            if not token:
                logger.critical(f'{token} недоступен!')
        return False


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    message = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if len(homework) > 0:
                current_message = parse_status(homework[0])
                if current_message != message:
                    send_message(bot, current_message)
                else:
                    logger.info('Статус работы не изменился')
                message = current_message
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except exceptions.InvalidResponceStatus:
            send_message(bot, 'Эндпойнт недоступен')
        except TypeError:
            send_message(bot, 'response не соответствует ожиданиям')
        except exceptions.DictKeyAbsence:
            send_message(bot, 'неверный ключ словаря')
        else:
            pass


if __name__ == '__main__':
    main()
