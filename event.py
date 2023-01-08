from collections import defaultdict
from enum import Enum, auto
from typing import Callable


events_storage = defaultdict(list)


class Event(Enum):
    STARTUP = auto()
    SHUTDOWN = auto()

    RESTART = auto()

    SAVE = auto()
    CLEAR_SAVED_DATA = auto()


def subscribe(event: Event, func: Callable, *args, **kwargs) -> None:
    """Подписка на событие"""
    global events_storage
    events_storage[event].append({func: (args, kwargs)})


def push_event(event: Event) -> None:
    """Вызов события"""
    for functions in events_storage[event]:
        for func in functions.items():
            func, data = func
            args, kwargs = data[0], data[1]
            func(*args)
