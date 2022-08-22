from math import exp

def sigmoid_thr(k1,k2,x):
    comp1 = 1 + exp(-k1*(x-k2))
    fx = 1/comp1
    return fx

def keramati_gutkin_reward(*deltas):
    rew=0
    for val in deltas:
        sign = val / abs(val)
        rew += val*val * sign
    return rew