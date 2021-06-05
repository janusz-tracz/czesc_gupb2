from __future__ import annotations
import collections
from dataclasses import dataclass
import logging
import random
from typing import Any, List, Optional

from tqdm import trange

from gupb2 import controller
from gupb2.model.profiling import PROFILE_RESULTS, print_stats
from gupb2.logger import core as logger_core
from gupb2.model import games

verbose_logger = logging.getLogger('verbose')


class Runner:
    def __init__(self, config: dict[str, Any]) -> None:
        self.controllers: list[controller.Controller] = config['controllers']
        self.runs_no: int = config['runs_no']
        self.scores: dict[str, int] = collections.defaultdict(int)
        self.profiling_metrics = config['profiling_metrics'] if 'profiling_metrics' in config else None

    def run(self) -> None:
        for i in trange(self.runs_no, desc="Playing games"):
            verbose_logger.info(f"Starting game number {i + 1}.")
            GameStartReport(i + 1).log(logging.INFO)
            self.run_game(i)

    def run_game(self, game_no: int) -> None:
        game = games.Game(self.controllers)
        self.run_in_memory(game)
        for name, score in game.score().items():
            logging.info(f"Controller {name} scored {score} points.")
            ControllerScoreReport(name, score).log(logging.DEBUG)
            self.scores[name] += score

    def print_scores(self) -> None:
        verbose_logger.info(f"Final scores.")
        scores_to_log = []
        for i, (name, score) in enumerate(sorted(self.scores.items(), key=lambda x: x[1], reverse=True)):
            score_line = f"{i + 1}.   {name}: {score}."
            verbose_logger.info(score_line)
            scores_to_log.append(ControllerScoreReport(name, score))
            print(score_line)
        FinalScoresReport(scores_to_log).log(logging.INFO)

        if self.profiling_metrics:
            for func in PROFILE_RESULTS.keys():
                print_stats(func, **{m: True for m in self.profiling_metrics})

    @staticmethod
    def run_in_memory(game: games.Game) -> None:
        while not game.finished:
            game.cycle()


@dataclass(frozen=True)
class GameStartReport(logger_core.LoggingMixin):
    game_number: int


@dataclass(frozen=True)
class ControllerScoreReport(logger_core.LoggingMixin):
    controller_name: str
    score: int


@dataclass(frozen=True)
class FinalScoresReport(logger_core.LoggingMixin):
    scores: List[ControllerScoreReport]
