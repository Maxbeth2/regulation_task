# Regulation Task
## A minimalist approach to investigating the relationship between physiological regulatory processes and cognition

[Video of agent performing task](https://www.youtube.com/watch?v=-LgDBbVABHQ)
--
<img src="images/Flowchart.png">

### Fig.1: The internal regulator
From bottom to top:
* A 'stream' of nutrients is flowing past the body of the agent. $[Nt-1, Nt, Nt+2,...]$
* The agent observes (among other things) the energy and waste contents in the stream at timestep $t$: $( WNt, ENt )$ and 
* has to decide whether or not to allow this nutrient to enter its body. ( $i$ )
* Once in the body, the nutrient is processed, releasing both the energy ( $Ei$ ) and waste products ( $Wi$ ) into the body. The amount of energy ( Ei ) extracted is modulated by three factors: 
  * the amount of energy originally present in nutrient: $(ENt)$
  * The amount of waste present in the body: $Pw(W)$
  * how much energy the system allocates to "digestion": $fE(f)$
    * As follows: $Ei = ENt * Pw * fE$
* The amount of waste added is equal to ( $WNt$ )
* Then waste is removed from the body $(Wo)$:  $W --> W-fW(f)$
* Energy is also "spent" at a constant rate $(Eo)$: $E --> E- bm$, where bm stands for "basal metabolism" 

---
* $f$ is an actuated variable, as is $i$
  * $f$ controls the proportion of energy directed to the $Ei$ and $Wo$ processes, where a low $f$ value means high waste excretion and a high $f$ value means efficient energy extraction.
  * $i$ controls whether or not a nutrient enters the body
* the sensed variables a given timestep are by default: $WNt, ENt, W, E, f, i$

---
## Installation

1. In terminal, navigate to root of repository (folder containing setup.py)

2. make sure you the python environment you wish to install to is activated in the terminal 

3. run command
   ```pip install -e .```



## Use

### in python:

```
import gym
import regulation_task

env = gym.make("RegulationTask-v0")
```


and there you have your environment.


## Adapt to RL

Currently, the reward function in the environment is adapted to evolutionary algorithms, giving a reward of 1 for each timestep that the agent is alive.
You can go to 'regulation_task.py' and change the reward function (located in the step method of RegulationTask)
One possible reward function can be implemented by accessing the energy level of the agent.


#### Reward based on staying alive
```
# within step method of regulation_task.py

if self.alive == True:
            reward = 1       # <-- where reward is set
            done = False
        else:
            reward = 0
            done = True
```
#### Reward based on energy level
```
# within step method of regulation_task.py

if self.alive == True:
            reward = self.body.E      # <-- get energy varialbe level of agent
            done = False
        else:
            reward = 0
            done = True
```



now the agent is rewarded according to how 'satiated' it is at each time step

