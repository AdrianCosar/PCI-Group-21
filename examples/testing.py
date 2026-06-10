from data_analysis import Humans, Diddler
from math import log

import polars as pl
from pygame.math import Vector2
from dataclasses import dataclass
from vi.config import Config
from vi import Agent, Config, HeadlessSimulation, Matrix
from vi.util import count
from config import WHITE_IMG, RED_IMG
from multiprocessing import Pool
class Simulation_headless_altered(HeadlessSimulation):
    def __init__(self, config , *args, **kwargs) -> None:
        super().__init__(config, *args, **kwargs)
        self._end_ticks = None
    def after_update(self) -> None:
        super().after_update()
        if not any(isinstance(agent, Humans) for agent in self._agents):
            self._end_ticks = self.shared.counter
            self.stop()

def run_simulation(config: Config) -> pl.DataFrame:
    sim = (
        Simulation_headless_altered(config)
        .batch_spawn_agents(100, Humans, [WHITE_IMG])
        .batch_spawn_agents(10  , Diddler, [RED_IMG])
    ) 
    sim.run()
    return pl.DataFrame({"end_ticks": [sim._end_ticks], "seed": [config.seed]})

if __name__ == "__main__":
    # We create a threadpool to run our simulations in parallel
    with Pool() as p:
        # The matrix will create four unique configs
        matrix = Matrix(Config, radius=[50], seed=[1, 2])

        # Create unique combinations of matrix values
        configs = matrix.to_configs(Config)

        # Combine our individual DataFrames into one big DataFrame
        df = pl.concat(p.map(run_simulation, configs))
        df.write_csv("testing.csv")