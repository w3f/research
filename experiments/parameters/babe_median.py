# The function find_params() returns all parameters of BABE with the median algorithm
# Play with the initial parameters to see the changes in parameters of BABE with the median algorithm

import math
import time
import hashlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom
import scipy.special

L = 94670777.9 #Life time of BABE in seconds
n = 1000.0 #number of validators
alpha = 0.67 #honest validators
alphaOp = 0.85
T = 6 #second
D = T/2.0 - 0.001 #network delay + 2 Sigma in terms of second where Sigma is a clock drift 
drift_in_one_day = 1 # second. according to http://www.ntp.org/ntpfaq/NTP-s-sw-clocks-quality.htm#AEN1220




######## PROBABILITIES ##########################################################

#finds the probability of only honest validators are selected
def prH(c, alpha):
    p = 1 - pow(1-c,1/n) #the probability of being a slot leader for a validator
    
    m = int(alpha * n)
    b = binom(m,p)
    sum = 0
    for k in range(1,m+1):
        sum = sum + b.pmf(k)
    return roundtwo(pow(1-c, 1-alpha) * sum)

#finds the probabolity that at least one validator is selected
def prh(c, alpha):
    p = 1 - pow(1-c,1/n) #the probability of being a slot leader for a validator
    
    return roundtwo(c - prM(c, alpha))

#finds the probability that only malicious validators are seleceted
def prM(c, alpha):
    p = 1 - pow(1-c,1/n) #the probability of being a slot leader for a validator
    
    m = int((1-alpha) * n)
    b = binom(m,p)
    sum = 0
    for k in range(1,m+1):
        sum = sum + b.pmf(k)
    return roundtwo(pow(1-c, alpha) * sum)
    
#finds the probability that at least one malicious validator is selected    
def prm(c, alpha):
    #print prH(c,alpha)
    return c - roundtwo(prH(c,alpha))

#finds the probability of only one honest validator is selected   
def prOneH(c,alpha):
    p = 1 - pow(1-c,1/n) #the probability of being a slot leader for a validator    
    return roundtwo(alpha * n * p * pow(1-p, n-1))

########################### END OF PROBABILITIES ################################

#Checks if the parameters above satisfies the condition of having more only ONE honest validator assigned slot than the others
def checkparams(cx):
    po = prOneH(cx, alpha)
    if po < 1 - (1- cx) - po:
        #print pdH
        return False
    else:
        return True

#Finds the maximum c value that satisfies the security conditions
def c_optimize():
    for cx  in np.arange(1,0,-0.01):
        cx = roundtwo(cx)
        if checkparams(cx) == True:
            return cx
 
 
c = c_optimize() #assign a new value if different c value is needed
#c = 0.25
pm = prm(c, alpha)
pM = prM(c, alpha)
pH = prH(c, alpha)
ph = prh(c, alpha)
pOneH = prOneH(c, alpha)

p_attack = 0.005 #the targetted attack probability of BABE
       
       
#Finds the probabalitity of attacking BABE with the median algorithm       
def pbabe(s_hcg, s_ecq, k, kcq,omega):    
    pcg = prcg(s_hcg,c,omega)
    pecq = precq(kcq)
    pcp = prcp(k,c)
    slots = math.ceil(L/T) # total number of slots in lifetime of BABE
    p = slots/(2 * s_ecq +s_hcg) * pow(2,20) * int(n * (1-alpha))* (pcg + pecq + pcp)
    return p



#Finds all the necessary parameters to satisfy the targetted attack probability
def find_params():
    if checkparams(c) == False:
        return "Parameters do not satisfy the condtion p_H /c> 0.5"
    p_babe = 1
    R = 0
    kcq = 1
    mu = 0
    s_hcq = 0
    s_ecq = 0
    mu_hcq = 0.54
    omega, gamma = find_omega_gamma(alphaOp, mu_hcq)
    p_babe = 1
    
    #it does the steps in https://hackmd.io/yXXiBoWMQe67szJk_PD9sw?both#BABE-with-the-Median-Algorithm until reaching the target attack probability
    while(p_babe > p_attack):
        kcq = kcq+1
        k = 8 * kcq 
        t_hcg = thcg(omega)
        s_hcg = shcg(k, t_hcg)
        t = tparam(k,kcq,s_hcg)
        s_ecq =  secq(kcq,t)
        s_hcq = shcq(s_ecq, mu_hcq)
        p_babe = pbabe(s_hcg,s_ecq,k,kcq,omega)
    sync_epoch = (s_hcq + 2 * s_ecq) * 6 / 60.0 / 60.0 # in terms of hour
    sigma = guessdrift(sync_epoch) #expected clock drift in every sync_epoch
    
    print '################### PARAMETERS OF BABE WITH THE MEDIAN ALGORITHM ###################'
    print 'c = ' + str(c) + ', slot time T = ' + str(T)
    print 'It is secure in ' + str(int(round(L * 3.16887646 * pow(10,-8),1))) + ' years with probability ' + str(1-p_babe)
    print 'It is resistant to '+ str(D-2 * sigma) + ' second network delay and'+ str(sigma)+ ' seconds drift in one sync-epoch'
    print '~~~~~~~~~~~~~~ Common Prefix Property ~~~~~~~~~~~~~~'
    print 'k = ' + str(k)
    print 'It means: Prun the last ' + str(k) + ' blocks of the best chain. All the remaining ones are probabilistically finalized'
    print '~~~~~~~~~~~~~~ Epoch Length ~~~~~~~~~~~~~~'
    print 'Sync-Epoch length should be at least ' + str(int(s_hcq + 2 * s_ecq)) + ' slots, ' + str(int(s_hcq + 2 * s_ecq)*T/60.0/60.0) + ' hours'
    print 'Epoch length should be at least ' + str(int(2 * s_ecq + s_hcg)) + ' slots,' + str(int(2 * s_ecq + s_hcg) * T/60.0/60.0)+' hours'
    print 'Probability of waiting more than 2D in the end of sync epoch is '+ str(prcq(s_hcq,gamma))
   


# finds the omega and gamma parameters in the HCG and HCQ properties that satisfies the conditions theorem 1 and theorem 2    
def find_omega_gamma(alphaOp, mu_hcq):
    pmOp = prm(c,alphaOp)
    for omega in np.arange(1,0,-0.01):
        t_hcg = thcg(omega)
        gamma = t_hcg * (1-mu_hcq)/pmOp - 1        
        if gamma > 0.1:
            print gamma
            return roundtwo(omega), roundtwo(gamma)
    print 'no good gamma and omega value is found'


############ PROBABILITIES OF BREAKING ONE OF THE SECURITY PROPERTIES OF BABE ############    
def thcg(omega):
    return ph  * (1-omega)

def shcg(k, t_hcg):
    return k / t_hcg

def tparam(k, kcq,s_hcg):
    return (k-2*kcq)/s_hcg 

def secq(kcq,t):
    return kcq / t

def muhcq(gamma, t_hcg):
    return 1- (pm * (1+gamma)/t_hcg)
def shcq(s_ecq, mu_hcq):
    return 2 * s_ecq / (2 * mu_hcq - 1)    
    

def prcg(s_hcg, c, omega):
    return math.exp(-(ph  * s_hcg * pow(omega,2))/2)

def precq(kcq):
    
    #k = (1-delta) * s_cq * c 
    #return math.exp(-c * s_cq * pow(delta,2)/2) * k/ 2 * pow(ph * pow(1-c, D),k)
    return math.exp(-kcq)
    
def prcq(s_hcq,gamma):
    pmOp = prm(c,alphaOp)
    return math.exp(-(pmOp * s_hcq * pow(gamma,2))/(2+gamma))
    
def prcp(k,c):
    return math.exp(-(k))
    
#Given a time in terms of hour, it finds the expected clock drift    
def guessdrift(h):
    return (drift_in_one_day * h)/(24.0)
    
    


def roundtwo(x):
    xr = round(x,2)
    if xr > x:
        xr  = xr - 0.01
    return xr        
    

    
