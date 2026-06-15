from data_analysis import Humans, Diddler, FlockingConfig
from math import log
import os
import csv
import polars as pl
from pygame.math import Vector2
from dataclasses import dataclass
from vi.config import Config
from vi import Agent, Config, HeadlessSimulation, Matrix
from vi.util import count
from config import WHITE_IMG, RED_IMG
from multiprocessing import Pool\

attraction_magnitude: int = 1

class Simulation_headless_altered(HeadlessSimulation): 
    """Altered version of the HeadlessSimulation class that allows us to access the end ticks after the simulation has stopped."""
    def __init__(self, config , *args, **kwargs) -> None:
        super().__init__(config, *args, **kwargs) 
        self._end_ticks = None
    def after_update(self) -> None:
        super().after_update() #i dont know if this is actually needed the documentation is not clear on if there are processes happening that need to so i just coppied them in, it seems to work, witohut it the times go up by 1000 ticks so theres some process in it dont touch
        if not any(isinstance(agent, Humans) for agent in self._agents): #checks if there are humans left
            self._end_ticks = self.shared.counter #saves the ticks to the simulation to be access it later
            self.stop() #stops the simulation in the same tick
 
def run_simulation(config: FlockingConfig) -> pl.DataFrame:
    """alterd code from the documentation to run the simulation as a function that can be called in parallel and returnes a dataframe with the info we are looking for"""
    sim = (
        Simulation_headless_altered(config)
        .batch_spawn_agents(100, Humans, [WHITE_IMG])
        .batch_spawn_agents(1  , Diddler, [RED_IMG])
    ) 
    sim.run() #put outside as it was overwriting the info
    return pl.DataFrame({"end_ticks": [sim._end_ticks], "seed": [config.seed]})

if __name__ == "__main__":
    # We create a threadpool to run our simulations in parallel
    for attraction_magnitude in [0, 0.5, 1, 1.5, 2]: #we want to test different attraction magnitudes to see how it affects the end ticks
        with Pool() as p:
            # The matrix will create four unique configs
            #matrix = Matrix(FlockingConfig, radius=[50], seed=list(range(1,2)), attraction_magnitude=[attraction_magnitude]) #sets the config parameters for the simulation

            # Create unique combinations of matrix values
            #configs = matrix.to_configs(Config)
            configs = [FlockingConfig(radius=160, seed=s, attraction_magnitude=attraction_magnitude)
                       for s in range(0,1999)]
            with Pool() as p, open(filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["end_ticks", "seed"])
                writer.writeheader()
                for result in p.imap(run_simulation, configs):
                    writer.writerow(result)
                    f.flush()  # flush after each row so it gets off my ram