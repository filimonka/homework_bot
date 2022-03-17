"""Custom errors for my bot."""


from requests.exceptions import RequestException


class JustLogErrors(Exception):
    """Общий класс для ошибок без отправки в телеграм."""

    def __init__(self):
        self.message = str(self.__doc__)
        super().__init__(self.message)


class AnyTelegramError(JustLogErrors):
    """Проблема отправки сообщения в телеграм."""

    pass


class ErrorLevelProblem(Exception):
    """Будем слать в телеграм сообщения."""

    def __init__(self):
        self.message = str(self.__doc__)
        super().__init__(self.message)


class AnyApiError(RequestException, ErrorLevelProblem):
    """Ошибки доступа к api practicum.yandex."""

    pass


class IncorrectApiAnswer(RequestException, ErrorLevelProblem):
    """Проблема доступа к API practicum.yandex."""

    def __init__(self, response):
        """Получаем подробности запроса."""
        self.response = response
        self.message = f'Url запроса: {self.response.url}'
        super().__init__(self.response, self.message)


class OtherApiError(AnyApiError, ErrorLevelProblem):
    """Другая ошибка доступа к API practicum.yandex."""

    def __init__(self):
        """Получаем url запроса."""
        self.message = self.__doc__
        super().__init__(self.message)


class IncorrectType(TypeError, ErrorLevelProblem):
    """Тип данных ответа api не соответствует ожиданиям."""

    pass


class ResponseKeyError(KeyError, ErrorLevelProblem):
    """В response отсутствует нужный ключ."""

    pass


class StatusKeyError(KeyError, ErrorLevelProblem):
    """Неизвестный статус работы."""

    pass
