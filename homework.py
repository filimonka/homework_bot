"""Бот Telegram проверяющий статус проверки проекта Я.Practicum."""


import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from requests.exceptions import (ConnectionError, HTTPError, RequestException,
                                 Timeout)

import exceptions

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


# Не придумала что в значениях, разве не статусы проверки?
HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def get_logger():
    """Настраиваем logger."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(funcName)s, %(lineno)s: %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def send_message(bot, message):
    """Отправка сообщения о статусе работы или ошибке."""
    logger.info('Отправляем сообщение.')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Сообщение отправлено.')
    except telegram.error.TelegramError as error:
        logger.error('Не удалось отправить сообщение', error, exc_info=True)


def get_api_answer(current_timestamp):
    """Получение ответа сервера."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        api_answer = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
        )
        if api_answer.status_code != HTTPStatus.OK:
            logger.warning(f'Url запроса: {api_answer.url}', exc_info=True)
            raise HTTPError()
        return api_answer.json()
    except ConnectionError:
        logger.warning('Проблема связи с сервером', exc_info=True)
        raise ConnectionError
    except Timeout:
        logger.warning('Время ожидания ответа истекло', exc_info=True)
        raise Timeout


def check_response(response):
    """Проверка полей ответа сервера."""
    if not isinstance(response, dict):
        raise exceptions.IncorrectType()
    try:
        response['homeworks']
        if not isinstance(response['homeworks'], list):
            raise exceptions.IncorrectType()
        return response['homeworks']
    except KeyError:
        raise exceptions.ResponseKeyError()


def parse_status(homework):
    """Получение данных о статусе работы."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError:
        raise exceptions.ResponseKeyError()
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except KeyError:
        raise exceptions.StatusKeyError()


def check_tokens():
    """Проверка доступности всех необходимых токенов."""
    tokens = (
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    )
    return all(tokens)


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Один из токенов недоступен!', exc_info=True)
        raise exceptions.CriticalError()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    message = ''
    logger.info('Бот запущен')
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                current_message = parse_status(homeworks[0])
                if current_message != message:
                    send_message(bot, current_message)
                    message = current_message
                else:
                    logger.debug('Статус работы не изменился')
            current_timestamp = int(time.time() - 10)
        except RequestException as error:
            logger.error(msg=(str(error.__doc__)), exc_info=True)
            send_message(bot, str(error.__doc__) + ' Подробности в WARNING')
        except KeyError as error:
            logger.error(str(error.__doc__), error, exc_info=True)
            send_message(bot, str(error.__doc__))
        except TypeError as error:
            logger.error(str(error.__doc__), error, exc_info=True)
            send_message(bot, str(error.__doc__))
        except Exception as error:
            logger.error('Неизвестное исключение', error, exc_info=True)
            send_message(bot, 'Наташа, мы всё уронили!')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logger = get_logger()
    main()
