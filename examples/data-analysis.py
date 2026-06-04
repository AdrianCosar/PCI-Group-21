from math import log

import polars as pl
from pygame.math import Vector2
from dataclasses import dataclass
from vi.config import Config

from vi import Agent, Config, Simulation
from vi.util import count

@dataclass
class FlockingConfig(Config):...

class Humans(Agent):
    def update(self) -> None:
        separation = Vector2(0, 0)
        alignment = Vector2(0, 0)
        cohesion = Vector2(0, 0)
        herd_speed: list[float] = []
        for agent,distance in self.in_proximity_accuracy():
            agent_pos = agent.pos
            agent_direction = agent.move
            if distance <= 5: # first zone where they increase distance between them
                move_away = self.pos-agent_pos #making negative vector of their postitions to move away
                if move_away.length() > 0: #cant normalize a vector of 0
                    separation += move_away.normalize() #making it normalized so they all have the same weight while acting
            elif distance <= 10 and isinstance(agent, Diddler): #second zone where agents direction is the direction of the other agents
                move_away = self.pos-agent_pos #making negative vector of their postitions to move away
                if move_away.length() > 0: #cant normalize a vector of 0
                    separation += move_away.normalize() #making it normalized so they all have the same weight while acting
            elif distance <= 10 and isinstance(agent, Humans): #second zone where agents direction is the direction of the other agents
                alignment += agent_direction.normalize() #has to normalize it so it doesnt overwrite the other vectors from seperation and cohesion
            elif distance <= 25 and isinstance(agent, Humans):
                toward = agent_pos - self.pos # making a postive vector to move towards the other agents current location
                if toward.length() >0:
                    cohesion += toward.normalize() #normalized to not overwrite the other vectors too much while adding to total
            if 5<=distance <= 10 and isinstance(agent, Humans):
                    herd_speed.append(agent.config.movement_speed)
        total = separation+alignment+cohesion #choses the direction to actually move taking the total of the normalized vectors
        if total.length() > 0:
            if len(herd_speed) > 0:
                self.config.movement_speed = min(self.config.movement_speed - log(len(herd_speed))*0.001, min(herd_speed)) #the more agents in the herd the slower they go, but it is a very small decrease in speed so they dont get stuck
            else:
                self.config.movement_speed = 0.5
            self.move = total.normalize() *self.config.movement_speed #sets the next move, normalized and times the movement speed otherwise the speed varies due to the vectors being totaled

class Diddler(Agent):
    def update(self) -> None:
        separation = Vector2(0, 0)
        alignment = Vector2(0, 0)
        cohesion = Vector2(0, 0)
        for agent,distance in self.in_proximity_accuracy():
            if distance <= 10 and isinstance(agent, Humans):
                agent.kill()
                child = self.reproduce()
                child.pos = self.pos + Vector2(10, 0)
                break
            agent_pos = agent.pos
            if distance <= 5 and isinstance(agent, Diddler): # first zone where they increase distance between them
                move_away = self.pos-agent_pos #making negative vector of their postitions to move away
                if move_away.length() > 0: #cant normalize a vector of 0
                    separation += move_away.normalize() #making it normalized so they all have the same weight while acting
            elif distance <= 20 and isinstance(agent, Humans):
                toward = agent_pos - self.pos # making a postive vector to move towards the other agents current location
                if toward.length() >0:
                    cohesion += toward.normalize() #normalized to not overwrite the other vectors too much while adding to total
        total = separation+alignment+cohesion #choses the direction to actually move taking the total of the normalized vectors
        self.config.movement_speed = 0.5
        if total.length() > 0:
            self.move = total.normalize() *self.config.movement_speed #sets the next move, normalized and times the movement speed otherwise the speed varies due to the vectors being totaled

print(
    # We're using a seed to collect the same data every time.
    Simulation(FlockingConfig(radius=20, seed=1,image_rotation=True))
    .batch_spawn_agents(
        100,
        Humans,
        images=[
            "examples/images/white.png",
            #"examples/images/red.png",
        ],
    )
    .batch_spawn_agents(
        1,
        Diddler,
        images=[
            #"examples/images/white.png",
            "examples/images/red.png",
        ],
    )
    .run()
    #.snapshots.group_by("frame")
    # Count the number of agents (per frame) that see at least one other agent (making them red)
    #.agg((pl.col("in_radius") > 0).sum().alias("# red agents"))
    #.select("# red agents")
    # Create a statistical summary including the min, mean and max number of red agents.
    #.describe(),
)
