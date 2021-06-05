from __future__ import annotations
from dataclasses import dataclass
import logging
import random
from typing import Iterator, NamedTuple, Optional

# noinspection PyPackageRequirements
import statemachine

from gupb2 import controller
from gupb2.logger import core as logger_core
from gupb2.model import characters

verbose_logger = logging.getLogger('verbose')

MIST_TTH: int = 5

ChampionDeath = NamedTuple('ChampionDeath', [('champion', characters.Champion), ('episode', int)])


class Game(statemachine.StateMachine):
    do_actions = statemachine.State('DoActions', value=9, initial=True)
    do_break = statemachine.State('DoBreak', value=1)

    cycle = do_actions.to(do_break) | do_break.to(do_actions)

    def __init__(
            self,
            to_spawn: list[controller.Controller],
    ) -> None:
        self.champions: list[characters.Champion] = self._spawn_champions(to_spawn)
        self.action_queue: list[characters.Champion] = []
        self.episode: int = 0
        self.deaths: list[ChampionDeath] = []
        self.finished = False
        super(statemachine.StateMachine, self).__init__()

    def on_enter_do_actions(self) -> None:
        if not self.action_queue:
            self._environment_action()
        else:
            self._champion_action()

    def on_enter_do_break(self) -> None:
        pass

    def score(self) -> dict[str, int]:
        if not self.finished:
            raise RuntimeError("Attempted to score an unfinished game!")
        return {death.champion.controller.name: score for death, score in zip(self.deaths, self._fibonacci())}

    def _spawn_champions(self, to_spawn: list[controller.Controller]) -> list[characters.Champion]:
        champions = []
        for controller_to_spawn in to_spawn:
            champion = characters.Champion()
            champion.assign_controller(controller_to_spawn)
            champions.append(champion)
            verbose_logger.debug(f"Champion for {controller_to_spawn.name}"
                                 f" spawned.")
            ChampionSpawnedReport(controller_to_spawn.name).log(logging.DEBUG)
        return champions

    def _environment_action(self) -> None:
        if self.champions:
            smallest_val = min(map(lambda champ: champ.last_value, self.champions))
            for champ in self.champions:
                if champ.last_value == smallest_val:
                    champ.get_hit()

        self._clean_dead_champions()
        self.action_queue = self.champions.copy()
        self.episode += 1
        verbose_logger.debug(f"Starting episode {self.episode}.")
        EpisodeStartReport(self.episode).log(logging.DEBUG)

    def _clean_dead_champions(self):
        alive = []
        for champion in self.champions:
            if champion.alive:
                alive.append(champion)
            else:
                champion.die()
                death = ChampionDeath(champion, self.episode)
                self.deaths.append(death)
        self.champions = alive

        if len(self.champions) == 1:
            verbose_logger.debug(f"Champion {self.champions[0].controller.name} was the last one standing.")
            LastManStandingReport(self.champions[0].controller.name).log(logging.DEBUG)
            champion = self.champions.pop()
            death = ChampionDeath(champion, self.episode)
            self.deaths.append(death)

            win_callable = getattr(champion.controller, "win", None)
            if win_callable:
                win_callable()

        if not self.champions:
            self.finished = True

    def _champion_action(self) -> None:
        champion = self.action_queue.pop()
        champion.last_value = champion.act()
        

    @staticmethod
    def _fibonacci() -> Iterator[int]:
        a = 1
        b = 2
        while True:
            yield a
            a, b = b, a + b


@dataclass(frozen=True)
class ChampionSpawnedReport(logger_core.LoggingMixin):
    controller_name: str


@dataclass(frozen=True)
class EpisodeStartReport(logger_core.LoggingMixin):
    episode_number: int


@dataclass(frozen=True)
class LastManStandingReport(logger_core.LoggingMixin):
    controller_name: str
