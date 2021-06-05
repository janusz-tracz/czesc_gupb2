from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from functools import partial
import logging
import random
from typing import NamedTuple, Optional, Dict

from gupb2 import controller
from gupb2.logger import core as logger_core

verbose_logger = logging.getLogger('verbose')

CHAMPION_STARTING_HP: int = 5


class ChampionDescription(NamedTuple):
    controller_name: str
    health: int


class Champion:
    def __init__(self) -> None:
        self.health: int = CHAMPION_STARTING_HP
        self.controller: Optional[controller.Controller] = None
        self.last_value = 10000

    def assign_controller(self, assigned_controller: controller.Controller) -> None:
        self.controller = assigned_controller

    def description(self) -> ChampionDescription:
        return ChampionDescription(self.controller.name, self.health)

    def act(self) -> None:
        if self.alive:
            action_val = self.pick_action()
            verbose_logger.debug(f"Champion {self.controller.name} got action value {action_val}.")
            ChampionPickedActionReport(self.controller.name, action_val).log(logging.DEBUG)
            return action_val
        else:
            return -100

    # noinspection PyBroadException
    def pick_action(self) -> Action:
        if self.controller:
            return self.controller.decide()
        else:
            return 0

    def die(self) -> None:
        verbose_logger.debug(f"Champion {self.controller.name} died.")
        ChampionDeathReport(self.controller.name).log(logging.DEBUG)

        die_callable = getattr(self.controller, "die", None)
        if die_callable:
            die_callable()
   
    def get_hit(self):
        self.health -= 1

    @property
    def alive(self):
        return self.health > 0


@dataclass(frozen=True)
class ChampionPickedActionReport(logger_core.LoggingMixin):
    controller_name: str
    value: int

@dataclass(frozen=True)
class ChampionDeathReport(logger_core.LoggingMixin):
    controller_name: str


@dataclass(frozen=True)
class ControllerExceptionReport(logger_core.LoggingMixin):
    controller_name: str
    exception: str
