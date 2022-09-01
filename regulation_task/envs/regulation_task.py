from random import randint, random
from time import sleep
from gym import Env
from gym.spaces.box import Box

import pygame as pg

import matplotlib.pyplot as plt
import numpy as np

from regulation_task.envs.bodySimpleMode import BodySimpleMode as Body
from regulation_task.envs.nutrientStream import NutrientStream
from regulation_task.envs.util_funcs.funcs import keramati_gutkin_reward

class RegulationTask(Env):
    def __init__(self):
        self.body = Body(nutrient_stream=NutrientStream())
        # Action space : [df, i]
        #self.action_space = Box(low=np.array([-1, -1]), high=np.array([1, 1]))
        self.action_space = Box(low = -1, high=1, shape=(2,))
        #self.action_space = Box(low = -1, high=1, shape=(1,))

        # Observation space : [E, T, E_Nt, W_Nt, f, i] 
        # Observation space : [E_Nt, W_Nt] 
        self.observation_space = Box(low=np.array([0, 0, 0, 0, -0.5, 0]), high=np.array([1, 1, 1, 1, 0.5, 1]), shape=(6,) )
        #self.observation_space = Box(low=0, high=1, shape=(1,) )

        
        self.alive = True
        self.stepno = 0

        self.collecting = False   # --------------|| Data pipeline
        self.reward_funcs = ["default", "cumulativeE", "keramati_gutkin"]
        self.reward_function = "cumulativeE"
        self.vary_noise = False
        print(f"\nUsing reward function: {self.reward_function}. run env.set_rf() for options..\n")
        

    def step(self, action):
        self.stepno += 1
        # keep track of deltaE for keramati gutkin rf
        prevE = self.body.E
        observation = self.body.time_step(action)
        currE = self.body.E

        if currE < 1:
            self.alive = False
        info={}
        if self.alive != True:
            reward = 0
            done = True
            return observation, reward, done, info

        if self.reward_function == "cumulativeE":
            reward = currE
        elif self.reward_function == "keramati_gutkin":
            deltaE = currE - prevE
            reward=keramati_gutkin_reward(deltaE)
        elif self.reward_function == "default":
            reward = 1
        done = False        
               
        return observation, reward, done, info


    def render(self):
        if self.collecting == False:      # --------------|| Data pipeline  
            self.start_data_colection()  
        else:
            self.register_timestep()

        # Pygame Render?


    def reset(self, seed=None, return_info=None, options=None):
        self.seed = seed
        if self.collecting:
            self.end_data_collection() # --------------|| Data pipeline
        self.body.reset()
        self.alive = True
        obs = self.body.get_obs()

        noise_amp = random() * 2
        noise_off = randint(-2,2)
        if self.vary_noise:
            self.climate_change()
        return obs

    def set_rf(self, rew_f=None):
        if rew_f == None:
            print("available reward funcs:\n")
            for rf in self.reward_funcs:
                print(rf)
            rew_f = str.strip(input("Enter desired reward function: "))
        if rew_f in self.reward_funcs:
            self.reward_function = rew_f
            print(f"\nSet reward function to {rew_f}!\n")

# below methods are for managing and visualising data

    def start_data_colection(self):  # --------------||
        self.collecting = True
        self.e_list = []
        self.w_list = []
        self.n_list = []
        self.f_list = []
        self.i_list = []
        self.pw_list = []


    def register_timestep(self, verbose=False):
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

        if verbose:
            print(f"E: {e}   W: {w}  N: {n}")
            print(f"i: {i}   f: {f}  pw: {pw}")
            print(LINE_UP, end=LINE_CLEAR)
            print(LINE_UP, end=LINE_CLEAR)
            sleep(0.1)


    def end_data_collection(self):  # --------------||
        # save run as numpy array
        self.collecting = False
        p = input("show plot? y/n: ")
        if p == 'y' or p == 'Y':
            self.quickplot()
        skip = self.save_run()
        if not skip:
            #self.mk_plots()
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


    def quickplot(self):
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
        print("\nYou will now get options to save and visualize the episode. close the figure to get options.\n")
        plt.show(block=True)
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
            mouth_closed_left_center = middle_w-20
            mouth_closed_right_center = middle_w+20
            mouth_height = middle_h - half_bs
            mouth_open = middle_w
            
            
            
            # ANIMATION LOOP
            for t in range(len(self.e_list)):
                bgc.g = int(self.n_list[t] * 8)
                screen.fill(bgc)

                ecirc_sz = self.e_list[t] / 4
                wcirc_sz = self.w_list[t] / 2
                p_color = self.pw_list[t] * 255
                #Body
                pg.draw.rect(screen, (100,100,100), body)
                pg.draw.rect(screen, (200,200,200), body, width=15)
                pg.draw.circle(screen,(p_color,200,0), e_circle_pos, ecirc_sz)
                # digestor
                # waste department
                pg.draw.circle(screen,(200,0,0), w_circle_pos, wcirc_sz)
                # flow indicator
                f_ind = self.f_list[t] * 40
                end_p = (middle_w+f_ind, middle_h)
                pg.draw.line(screen, red, anchor, end_p, 5)
                # open/close mouth
                if self.i_list[t] > 0.5:
                    left_mouth = pg.Rect(mouth_closed_left_center, mouth_height, 15, 30)
                    right_mouth = pg.Rect(mouth_closed_right_center,mouth_height, 15, 30)
                else:
                    left_mouth = pg.Rect(mouth_open, mouth_height, 15, 30)
                    right_mouth = pg.Rect(mouth_open,mouth_height, 15, 30)

                pg.draw.rect(screen, (255,100,100), left_mouth)
                pg.draw.rect(screen, (255,100,100), right_mouth)

                sleep(0.05)
                pg.display.flip()
                                         
            pg.display.flip()
            screen.fill(black)
            pg.display.flip()


    def save_run(self):
        choice = input("Options:\n-press ENTER to discard\n-enter desired filename to save data\n-add ', -v' to immediately plot and visualise: ")
        skip = True
        if ',' in choice:
            choice = choice.split(',')[0].strip()
            skip = False

        if choice != '':
            data = np.array( [self.e_list, self.w_list, self.n_list, self.f_list, self.i_list, self.pw_list] )
            choice = "lifecycles_data/" + choice
            np.save(choice, data, True)

        if choice == '':
            skip = True

        return skip



    def climate_change(self):
        ns = self.body.nutrient_stream
        ns.noise_amplitude_gen = randint(-ns.noise_amplitude, ns.noise_amplitude)
        ns.noise_offset_gen = randint(-ns.noise_offset, ns.noise_offset)

        print(f"generation noise | amp: {ns.noise_amplitude_gen} / {ns.noise_amplitude}, offs: {ns.noise_offset_gen} / {ns.noise_offset}")
    