from enum import Enum, auto
from random import randint

from save import init_save_system_decorator
from event import Event
import event


class Level:
    def __init__(self):
        self.__number = 0
        self.id = -2

    @property
    def number(self):
        return self.__number

    def increment(self):
        self.__number += 1

    def __repr__(self):
        return str(self.__number)


class State(Enum):
    ALIVE = auto()
    DEAD = auto()


class Enemy:
    def __init__(self, name: str, id_: int, hp: int):
        self.state = State.ALIVE
        self.name = name
        self.hp = hp
        self.id = id_

    def decrement_hp(self):
        self.hp -= 1
        if self.hp <= 0:
            print(f"{self.name}-{self.id} is dead")
            self.state = State.DEAD
        elif self.hp > 1:
            print(f"{self.name}-{self.id} HP: {self.hp}")

    def is_dead(self) -> bool:
        return True if self.state is State.DEAD else False

    def __repr__(self):
        if self.is_dead():
            return "X"
        return f"{self.name}-{self.id}: {self.hp}"


class Battle:
    @init_save_system_decorator
    def __init__(self, level: Level):
        self.id = -1
        self.level = level
        self.enemies = []

    def generate_battle(self):
        self.level.increment()
        self.enemies = [Enemy("Demon", id_=number, hp=randint(1, 5)) for number in range(1, self.level.number + 1)]

    def all_enemies_is_dead(self) -> bool:
        return all(map(lambda enemy: enemy.state is State.DEAD, self.enemies))


def init_battle():
    print("\nStart")
    level = Level()
    battle = Battle(level)
    restart = False
    if len(battle.enemies) <= 0:
        battle.generate_battle()

    while restart is False:
        print(f"Level: {battle.level}")
        enemies = battle.enemies
        while not battle.all_enemies_is_dead():
            print(*enemies, sep="\t")
            input_data = input(f"\nHit enemy: 1-{len(enemies)} (Enter=Exit; R=Restart) --> ")
            if input_data.lower() == "r":
                restart = True
                break

            if not bool(input_data):
                event.push_event(Event.SHUTDOWN)

            enemies[int(input_data) - 1].decrement_hp()
            print()

        if restart: break
        battle.generate_battle()
        event.push_event(Event.SAVE)

    if restart:
        del battle
        event.push_event(Event.CLEAR_SAVED_DATA)
        event.push_event(Event.RESTART)


def main():
    event.push_event(Event.STARTUP)
    event.subscribe(Event.SHUTDOWN, exit)
    event.subscribe(Event.RESTART, init_battle)

    init_battle()


if __name__ == "__main__":
    main()
