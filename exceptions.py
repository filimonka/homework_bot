"""
Custom errors for my bot.
Спасибо за подсказку! Идею поняла. Мне кажется я её реализовала
в перехватывании RequestException  и KeyError.
"""


class IncorrectType(TypeError):
    """Формат ответа от api не соответствует ожиданиям."""

    pass


class ResponseKeyError(KeyError):
    """В response отсутствует нужный ключ."""

    pass


class StatusKeyError(KeyError):
    """Неизвестный статус работы."""

    pass


class CriticalError(Exception):
    """Отсутствует один из токенов, работа невозможна."""

    pass
