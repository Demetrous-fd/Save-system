from functools import wraps
from pathlib import Path
from os import getenv
import shelve

from event import Event
import event

save_path = Path(getenv("SSS_path", "saves"))
if not save_path.exists():
    save_path.mkdir(parents=True)

save_filename = Path(getenv("SSS_filename", "save"))
FULL_PATH = str((save_path / save_filename).absolute())


class SaveSystem:
    __instance = None
    __init = False
    __stack = list()

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(SaveSystem, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        if self.__init is False:
            event.subscribe(Event.SHUTDOWN, self.save_states)
            event.subscribe(Event.SAVE, self.save_states)
            event.subscribe(Event.CLEAR_SAVED_DATA, self.clear_saved_data)
            self.__init = True

    def add_object(self, obj):
        """Добавление объекта в список на сохранение"""
        self.__stack.append(obj)

    def save_obj_state(self, obj):
        """Сохранение объекта"""
        data = obj.__dict__.copy()
        name = obj.__class__.__name__
        with shelve.open(FULL_PATH, "c") as file:
            file[f"{name}-{obj.id}"] = data
        print(f"{name.title()}-{obj.id} saved, {data}")

    def save_states(self):
        """Сохранение всех объектов"""
        for obj in self.__stack:
            self.save_obj_state(obj)
        self.__stack.clear()
        print("Data saved")

    def load_state(self, obj) -> dict | None:
        """Выгрузка объекта из файла сохранения"""
        with shelve.open(FULL_PATH, "c") as file:
            return file.get(f"{obj.__class__.__name__}-{obj.id}", None)

    def clear_saved_data(self):
        """Очистка сохранения"""
        with shelve.open(FULL_PATH, "c") as file:
            file.clear()
        self.__stack.clear()


def load_saved_obj_state(obj: object, save_system: SaveSystem = SaveSystem()):
    """Восстанавливает состояние объекта, если данные были сохранены"""
    saved_data = save_system.load_state(obj)
    if saved_data is None:
        return

    old_data = obj.__dict__
    old_data.update(saved_data)


def init_save_system_decorator(method):
    """Декоратор для инициализации системы сохранения в классе, применяется к методу __init__"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if getattr(self, "id", None) is None:
            raise ValueError("В классе должен быть уникальный атрибут id !!!")

        method(self, *args, **kwargs)
        save_system = SaveSystem()
        load_saved_obj_state(self, save_system)
        save_system.add_object(self)
    return wrapper
