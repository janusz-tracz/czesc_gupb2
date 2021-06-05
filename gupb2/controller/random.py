import random

POSSIBLE_ACTIONS = range(0, 1000)

class RandomController:
    def __init__(self, first_name: str):
        self.first_name: str = first_name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RandomController):
            return self.first_name == other.first_name
        return False

    def __hash__(self) -> int:
        return hash(self.first_name)

    def reset(self) -> None:
        pass

    def decide(self):
        return random.choice(POSSIBLE_ACTIONS)

    @property
    def name(self) -> str:
        return f'RandomController{self.first_name}'
