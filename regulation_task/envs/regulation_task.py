from cmath import e
from time import sleep
from gym import Env
from gym.spaces.box import Box

import pygame as pg

import numpy as np
import matplotlib.pyplot as plt

from regulation_task.envs.bodySimpleMode import BodySimpleMode as Body
from regulation_task.envs.nutrientStream import NutrientStream

class RegulationTask(Env):
    def __init__(self, compartments=["w_comp","e_comp"], verbose=True):
        # Action space : [df, i]
        self.action_space = Box(low=np.array([-1, -1]), high=np.array([1, 1]), dtype=np.int8)

        # Observation space : [E, T, E_Nt, T_Nt, f] 
        self.observation_space = Box(low=np.array([0, 0, 0, 0, -0.5, 0]), high=np.array([100, 100, 30, 30, 0.5, 1]), shape=(6,) )
        
        compartments = compartments
        self.body = Body(compartments, food_stream=NutrientStream())
        self.alive = True
        self.stepno = 0
        self.verbose = verbose

        self.collecting = False   # --------------||
        
        

    def step(self, action):
        self.stepno += 1
        observation = self.body.time_step(action)
        if observation[0] < 1:
            self.alive = False
        info={}
        if self.alive == True:
            reward = 1
            done = False
        else:
            reward = 0
            done = True
               

        return observation, reward, done, info


    def render(self):
        if self.collecting == False:
            self.start_data_colection()  # --------------||

        LINE_UP = '\033[1A'
        LINE_CLEAR = '\x1b[2K'

        e = round(self.body.E,2)
        w = round(self.body.W,2)
        n = self.body.N
        f = round(self.body.f, 3)
        i = self.body.i
        pw = round(1-self.body.Pw,2)

        self.e_list.append(e)  # --------------||
        self.w_list.append(w)
        self.n_list.append(n[0])
        self.f_list.append(f)
        self.i_list.append(i)
        self.pw_list.append(pw)
        
        print(f"E: {e}   W: {w}  N: {n}")
        print(f"i: {i}   f: {f}  pw: {pw}")
        print(LINE_UP, end=LINE_CLEAR)
        print(LINE_UP, end=LINE_CLEAR)
        
        
        #sleep(0.0001)


    def reset(self):
        if self.collecting:
            self.end_data_collection() # --------------||
        self.body.reset()
        self.alive = True
        obs = self.body.time_step(self.action_space.sample())
        return obs

    def start_data_colection(self):  # --------------||
        self.collecting = True
        self.e_list = []
        self.w_list = []
        self.n_list = []
        self.f_list = []
        self.i_list = []
        self.pw_list = []

    def end_data_collection(self):  # --------------||
        self.collecting = False
        self.mk_plots()
        self.pygame_render()
        
    def mk_plots(self):

        plotname = input("Plotting... write plot filename + .png or press ENTER to skip: ")
        if plotname:
            t = range(len(self.e_list))
            a = plt.subplot(211)
            plt.plot(t, self.e_list, label="Energy")
            plt.plot(t, self.w_list, label="Waste")
            plt.plot(t, self.n_list, label="Nutritional value")
            plt.legend()
            b = plt.subplot(212)
            plt.plot(t, self.f_list, label="Flow")
            plt.plot(t, self.i_list, label="Mouth open/closed")
            plt.plot(t, self.pw_list, label="Waste penalty")
            plt.legend()
            plt.savefig(fname=plotname, format='png')
            plt.close()
    
    def pygame_render(self):
        render = input("Show animation? Y/N: ")
        if render == 'Y' or render == 'y':
            pg.init()
            size = width, height = 720, 720
            middle_h = height/2
            middle_w = width/2
            anchor = middle_w, middle_h-100
            black = 0, 0, 0
            bgc = pg.Color(0,0,0)
            red = pg.Color(255,0,0)
            screen = pg.display.set_mode(size)
            bodysize = 300
            half_bs = bodysize / 2
            body_pos = middle_w - half_bs, middle_h - half_bs
            e_circle_pos = (middle_w + 100, middle_h)
            w_circle_pos = (middle_w - 100, middle_h)
            body = pg.Rect(body_pos[0], body_pos[1], bodysize, bodysize)

            # ANIMATION LOOP
            for t in range(len(self.e_list)):
                bgc.g = int(self.n_list[t] * 8)
                screen.fill(bgc)

                ecirc_sz = self.e_list[t] / 4
                wcirc_sz = self.w_list[t] / 2
                p_color = self.pw_list[t] * 255
                #Body
                pg.draw.rect(screen, (200,200,200), body)
                # digestor
                pg.draw.circle(screen,(p_color,200,0), e_circle_pos, ecirc_sz)
                # waste department
                pg.draw.circle(screen,(200,0,0), w_circle_pos, wcirc_sz)
                # flow indicator
                f_ind = self.f_list[t] * 40
                end_p = (middle_w-f_ind, middle_h)
                pg.draw.line(screen, red, anchor, end_p, 5)
                sleep(0.05)
                pg.display.flip()   
            
            pg.display.flip()
            screen.fill(black)
            pg.display.flip()

