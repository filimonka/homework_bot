"""Custom errors for my bot."""


from requests.exceptions import RequestException, HTTPError


class JustLogErrors(Exception):
    """Общий класс для ошибок без отправки в телеграм."""

    pass


class AnyTelegramError(JustLogErrors):
    """Проблема отправки сообщения в телеграм."""

    pass


class ErrorLevelProblem(Exception):
    """Будем слать в телеграм сообщения."""

    pass


class IncorrectApiAnswer(HTTPError, ErrorLevelProblem):
    """Проблема http ответа practicum.yandex."""

    def __init__(self, *args, **kwargs):
        """Получаем подробности запроса."""
        self.response = kwargs.pop('response', None)
        self.message = f'Url запроса: {self.response.url}, {self.__doc__}'
        super(IncorrectApiAnswer, self).__init__(*args, **kwargs)


class OtherApiError(RequestException, ErrorLevelProblem):
    """Другая ошибка доступа к API practicum.yandex."""

    pass


class IncorrectType(TypeError, ErrorLevelProblem):
    """Тип данных ответа api не соответствует ожиданиям."""

    pass


class ResponseKeyError(KeyError, ErrorLevelProblem):
    """В response отсутствует нужный ключ."""

    pass


class StatusKeyError(KeyError, ErrorLevelProblem):
    """Неизвестный статус работы."""

    pass
