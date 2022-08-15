

from math import sin
from random import randint

class NutrientStream():
    """
    A type of flower is most nutricious when ripe, but needs to occasionally be eaten prematurely for short term survival. 
    However if the agents decides to eat too many flowers at these critical phases of the season, the
    abundance of available nutrients at the mature flower stage will be lower and thus may not provide enough energy to survive the winter.

    Things that affect nutrient avialability:\n
    Season - Sine function\n
    Noise ,test different amplitude- randomness?\n
    Agent forgaing - stochastic or simulated?\n

    """
    def __init__(self, dt=0.1):
        self.t = 0.0
        self.dt = dt
    
    def time_step(self):
        self.t += self.dt
        noise_amplitude = 0
        noise = randint(-2,noise_amplitude)
        amplitude = 8
        offset = 7
        self.val = max(amplitude * sin(self.t) + offset, 0)
        waste_val = max(4 * sin(self.t+0.5) + 3, 0)
        
        return (self.val, 4.8)
        
    
