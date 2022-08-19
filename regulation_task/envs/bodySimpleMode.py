from time import sleep
from regulation_task.envs.util_funcs.funcs import sigmoid_thr
import numpy as np
# compartmentalisation enables isolation of chemical reactions
# as well as selective resource flows towards processes
# deemed to be of biggest importance at the current time.
# The isolation of chemical reaction is not explicitly modeled here,
# but resource flows are modeled.
class BodySimpleMode():
    """
    Object that manages interactions between compartments 
    as well as compartments and environment.\n
    Attributes:\n
    d  | number of digestive compartments = max amt of nutrients that can be simultaneously drawn from N, dtype=int\n
    c  | number of cleaning compartments = max amt of toxins that can be cleared from system in one step\n
    bm | basal metabolism\nj

    """
    def __init__(self, compartments=["w_comp","e_comp"], food_stream=None):

       # SETUP ->
       
       # list of compartments within system
        self.compartments = compartments
        self.n_comps = len(compartments)

        self.w_comps = 0
        self.e_comps = 0
        self.bm = self.n_comps
        for comp in compartments:
            if comp == "w_comp":
                self.w_comps += 1
            if comp == "e_comp":
                self.e_comps += 1

        # the nutrient generating process
        self.food_stream = food_stream

        # buffer "curve shape" constants
        self.thr_k1 = -0.5
        self.thr_k2 = 70
        
        # sensed-only vars -------------
        self.N = (0,0) # sense limited no of elements, perhaps stochastically drawn
        self.W = 0.0
        self.E = 0.0
        # Sensed and Actuated vars ------------
        self.f = 0.0
        self.i = False
        
        # modulatory vars
        self.fW = 0.5
        self.fE = 0.5


    def time_step(self, action):

        """Order of operations:
        \n 1. Get and perform actions
        \n 2. cal3. Execute Wi and Ei
        \n 4. Execute Wo and Eo
        \n 5. Return observation of state"""
        
        self.i = False
        if action[0] > 0: # gym action
            self.i = True
    
        self.f += (action[1])/50      # gym action
        self.f = min(0.5,(max(-0.5, self.f)))
        
        # calculate modulators
        self.fW = 0.5 - self.f
        self.fE = 0.5 + self.f
        self.Pw = ( sigmoid_thr(self.thr_k1, self.thr_k2, self.W) ) # waste penalty

        # Execute Wi and Ei
        self.Wi_Ei()
        # Execute Wo and Eo
        self.Wo_Eo()

        # get next food for next observation / action
        next_food = self.food_stream.time_step()
        self.N = next_food

        # get observation to act on in next time step
        sys_vars = self.get_obs(next_food)
        return sys_vars


    def Wi_Ei(self):
        """Applies additive operations to system variables
        \n Wi : waste in
        \n Ei : energy in"""
        if self.i and self.N != None:
            add_E_lv = self.N[0]
            self.E += (add_E_lv * self.Pw * self.f)
            self.W += self.N[1] * self.f
            self.N = None
    

    def Wo_Eo(self):
        """Applies subtractive operations to system variables
        \n Wo : waste out
        \n Eo : energy out"""
        if self.W > 3:
            self.W -= (self.w_comps * (self.fW))
        self.E -= self.bm # pay cost of basal metabolism


    def reset(self):
        #print("RESETTING")
        self.E = 30
        self.W = 30
        self.N = None
        self.f = 0
        self.i = False
        self.food_stream.t = 0


    def get_obs(self, next_food=None):
        """ returns a np array containing the observation of the current state"""
        if next_food != None:
            next_E = next_food[0]
            next_W = next_food[1]
        else:
            next_E = 0
            next_W = 0

        return np.array([self.E, self.W, next_E, next_W, self.f, self.i], dtype='float32')

    def display_status(self, sleeptime=0.1):
        E = round(self.E, 2)
        W = round(self.W, 2)
        Ne = round(self.N[0],2)
        Nw = round(self.N[1],2)
        i = self.i
        f = round(self.f,2)
        print(f"\rBody status | E: {E}  W: {W}  i: {i}  r: {f}  Ne: {Ne}  Nw: {Nw}",end='')
        sleep(sleeptime)

    def info(self):
        print(f"Body with {len(self.compartments)} compartments.")
        i = 1
        for comp in self.compartments:
            print(f"\Compartment {i} info: {comp.ret_info()}")
            i+=1