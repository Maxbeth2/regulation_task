

from math import sin
from random import randint, random, randrange

class NutrientStream():
    """
    A type of flower is most nutricious when ripe, but needs to occasionally be eaten prematurely for short term survival. 
    However if the agents decides to eat too many flowers at these critical phases of the season, the
    abundance of available nutrients at the mature flower stage will be lower and thus may not provide enough energy to survive the winter.

    """
    def __init__(self, dt=0.1):
        self.t = 0.0
        self.dt = dt

        self.amplitude = 8
        self.offset = 7
        self.noise_amplitude = 0
        self.noise_offset = 0
    
    def time_step(self):
        self.t += self.dt
        
        noise = ((random() - 0.5) * 2 * self.noise_amplitude) + self.noise_offset
        offset = self.offset
        self.val = max(self.amplitude * sin(self.t) + offset + noise, 0)
        
        waste_val = max(4 * sin(self.t+0.5) + 3, 0)
        
        return (self.val, 4)
        
    
