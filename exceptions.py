"""Custom errors for my bot."""


class InvalidResponceStatus(Exception):
    """Ошибка статуса http ответа."""

    def __init__(
            self,
            response,
            message='Статус ответа отличается от HTTPStatus.OK'
    ):
        self.response = response
        self.message = message
        super.__init__(self.message)


class DictKeyAbsence(Exception):
    """Отсутствует необходимый ключ словаря."""

    pass
