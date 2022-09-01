

from math import radians, sin
from random import randint, random, randrange

class NutrientStream():
    """
    A type of flower is most nutricious when ripe, but needs to occasionally be eaten prematurely for short term survival. 
    However if the agents decides to eat too many flowers at these critical phases of the season, the
    abundance of available nutrients at the mature flower stage will be lower and thus may not provide enough energy to survive the winter.

    """
    def __init__(self, dt=6):
        self.t = 0.0
        self.dt = dt

        self.amplitude = 4
        self.offset = 8
        
        #max values of noise
        self.noise_amplitude = 0
        self.noise_offset = 0
        
        # noise levels for current generation
        self.noise_offset_gen = 0
        self.noise_amplitude_gen = 0

    def time_step(self):
        self.t += self.dt
        
        if self.noise_amplitude_gen == 0 and self.noise_offset_gen == 0:
            noise = self.noise_offset + ((random() - 0.5) * 2 * self.noise_amplitude)
        else:
            noise = self.noise_offset_gen + ((random() - 0.5) * 2 * self.noise_amplitude_gen)
        #print(noise)
        offset = self.offset
        time_of_year = radians(self.t)
        self.val = max(self.amplitude * sin(time_of_year) + offset + noise, 0)
        
        waste_val = max(4 * sin(self.t+0.5) + 3, 0)
        
        return (self.val, 5)
        
    

# ns = NutrientStream()

# sums=0
# wst=0
# for i in range(360):
#     val, v2 = ns.time_step()
#     sums+=val
#     wst+=v2

# print(sums)
# print(wst)
