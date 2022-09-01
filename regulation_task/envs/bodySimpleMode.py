from random import randint
from time import sleep
from regulation_task.envs.nutrientStream import NutrientStream
from regulation_task.envs.util_funcs.funcs import sigmoid_thr
import numpy as np
# compartmentalisation enables isolation of chemical reactions
# as well as selective resource flows towards processes
# deemed to be of biggest importance at the current time.
# The isolation of chemical reaction is not explicitly modeled here,
# but resource flows are modeled.
class BodySimpleMode():
    """### A body needs nutrients to keep going, and it needs to rid the system of excess waste products in order to function properly.\n
    State of operation:\n
    * The body can choose whether or not to be permeable to its surroundings by opening or closing its "mouth" - bool ( i ).\n
    * If the mouth is open, a "token" of nutrients tuple ( E_nt, W_nt ) arrive into the system.\n
    * The body then processes these nutrients, resulting in the addition of both energy float ( E ) (which keeps the body operational)
    and waste float ( W ), that the body must get rid of.
    * How much E and W are added to the system upon consumption of nutrients depends on several things:
    \n\t\t* How much Energy and Waste the nutrient token contains
    \n\t\t* How much waste is already in the system ( 'waste penalty' / Pw ) 0 < Pw < 1; The energy gained from processing a nutrient is multiplied by Pw
    \n\t\t* A regulatoy variable 'f' (stands for flow, or focus if you like) which represents how the body regulates itself and directs its energy.
    \n\t\t\t* -0.5 < f < 0.5. 
    \n\t\t\t* The greater f is, the more resources are directed towards extracting enegy from the incoming nutrients
    \n\t\t\t* The smaller f is, the more resources are directed towards excreting waste from the system
    \n * The body processes the nutrient, adds/substracts the correct amounts of E and W to/from the system.
    \n * The process repeats, with new nutrients arriving and the agent deciding whether to consume them and how to process them while maintaining its system variables (E and W)
    \n * The gym env checks the body's E variable and sets done = True if it goes under a threshold (1)
    """
    def __init__(self, compartments=["w_comp","e_comp"], nutrient_stream=NutrientStream()):

       # SETUP ->
        self.sense_internal_vars = True
        self.sense_external = True
        self.sense_actuatory_states = True
       # list of compartments within system - overcomplicated way of specifying that the system can extract energy and excrete waste
        self.compartments = compartments

        self.w_comps = 0 # w_comp can be read as "capability to excrete waste"
        self.e_comps = 0 # e_comp can be read as "capability to extract energy"
        self.basal_metabolsim = 1.2 # how much energy is used by the system per time step
        self.waste_clear_rate = 1
        for comp in compartments:
            if comp == "w_comp":
                self.w_comps += 1
            if comp == "e_comp":
                self.e_comps += 1

        # the nutrient generating process
        self.nutrient_stream = nutrient_stream
        """calling the time_step() of nutrient_stream returns a nutrient"""

        # buffer "curve shape" constants
        self.thr_k1 = -0.5
        """sets 'slope' of threshold"""
        self.thr_k2 = 50
        """midpoint of threshold (where waste penalty is 0.5)"""
        
        # sensed-only vars -------------
        self.N = (0,0)
        """The nutrient the agent is currently considering \n\n ## Sensed"""
        self.maxW = 120
        self.W = 0.0
        """Current level of waste in body \n\n ## Sensed"""
        self.maxE = 120
        self.E = 0.0
        """Current level of energy stored in body \n\n ## Sensed"""
        # Sensed and Actuated vars ------------
        self.f = 0.0
        """parameter that decides the proportion of energy going to each 'bodily function', controlling their effetiveness. \n\n ## Sensed \n\n ## Actuated"""
        self.i = False
        """bool that if true means the agent will take the currently considered nutrient into the system and process it. \n\n ## Sensed \n\n ## Actuated"""
        
        # modulatory vars 
        self.fW = 0.5 # affects efficiency of waste excretion
        """the amount of waste excreted from the body in a timestep is multiplied by this variable"""
        self.fE = 0.5 # affects efficiency of energy extraction
        """the amount of energy extracted from a nutrient is multiplied by this variable"""
        self.Pw = 1
        """a function of W, thr_k1, and thr_k2. The amount of energy extracted from a nutrient is multiplied by this variable """


    def time_step(self, action):

        """Order of operations:
        \n 1. Get and perform actions
        \n 2. cal3. Execute Wi and Ei
        \n 4. Execute Wo and Eo
        \n 5. Return observation of state"""
        
        self.i = False
        if action[0] > 0: # gym action
            self.i = True

        try:
            self.f += (action[1])/50      # gym action
            self.f = min(0.5,(max(-0.5, self.f)))
        except:
            self.f = 0.0
        
        # calculate modulators
        self.fW = 0.5 - self.f
        self.fE = 0.5 + self.f
        self.Pw = ( sigmoid_thr(self.thr_k1, self.thr_k2, self.W) ) # waste penalty

        # Execute Wi and Ei
        self.Wi_Ei()
        # Execute Wo and Eo
        self.Wo_Eo()

        # get next nutrient for next observation / action
        self.N = self.nutrient_stream.time_step()

        # get observation to act on in next time step
        observation = self.get_obs()
        return observation


    def Wi_Ei(self):
        """Applies additive operations to system variables
        \n conditions : do if "mouth" is open (i=True) and nutrient is available
        \n * Wi : waste in ; Ei : energy in
        \n Waste in = waste contained in nutrient
        \n Energy in = energy in nutrient * waste penalty * regulated activity (f)"""
        if self.i and self.N != None:
            add_E_lv = self.N[0]
            self.E += (add_E_lv * self.Pw * self.fE) # * self.e_comps
            self.E = min(self.E, self.maxE)
            self.W += self.N[1]
            self.N = None
    

    def Wo_Eo(self):
        """Applies subtractive operations to system variables
        \n Wo : waste out
        \n Eo : energy out"""
        
        self.W -= (self.waste_clear_rate * self.fW) # * self.w_comps
        self.W = max(0, self.W)
        self.E -= self.basal_metabolsim # pay cost of basal metabolism


    def reset(self):
        """resets the bodies variables, should be called by env's reset()\n
        TODO: make stochastic option
        """
        #print("RESETTING")
        self.E = 30 #+ randint(-5,5)
        self.W = 30 #+ randint(-5,5)
        self.N = None
        self.f = 0
        self.i = False
        self.nutrient_stream.t = 0


    def get_obs(self):
        """ returns a np array containing the observation of the current state"""
        next_E = 0
        next_W = 0
        if self.N != None:
            next_E = self.N[0]
            next_W = self.N[1]
        max_Ent = self.nutrient_stream.amplitude + self.nutrient_stream.offset + self.nutrient_stream.noise_amplitude
        return np.array([self.E/self.maxE, self.W/self.maxW, next_E/max_Ent, 1, self.f, self.i], dtype='float32')
        #return np.array([next_E/max_Ent], dtype='float32')

    def get_max_vals(self):
        pass

    def display_status(self, sleeptime=0.1):
        """Prints out some variables of the body in a pretty fashion"""
        E = round(self.E, 2)
        W = round(self.W, 2)
        Ne = round(self.N[0],2)
        Nw = round(self.N[1],2)
        i = self.i
        f = round(self.f,2)
        print(f"\rBody status | E: {E}  W: {W}  i: {i}  r: {f}  Ne: {Ne}  Nw: {Nw}",end='')
        sleep(sleeptime)

    # def info(self):
    #     print(f"Body with {len(self.compartments)} compartments.")
    #     i = 1
    #     for comp in self.compartments:
    #         print(f"\Compartment {i} info: {comp.ret_info()}")
    #         i+=1