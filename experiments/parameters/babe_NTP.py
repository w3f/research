# The function find_params() returns all parameters of BABE with NTP
# Play with the initial parameters to see the changes in parameters of BABE with NTP
import math
import time
import hashlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom
import scipy.special

L = 94670777.9 #Life time of BABE in seconds
n = 1000.0 #number of validators
#c = 0.25 #either set yourself or use the c_optimize function below to find the optimum c value
alpha = 0.67 #honest validators
T = 6 #second
delta_max = 6
D = math.floor(delta_max/T)



def roundtwo(x):
    xr = round(x,2)
    if xr > x:
        xr  = xr - 0.01
    return xr 

######## PROBABILITIES ##########################################################

#finds the probability of only honest validators are selected
def prH(c, alpha):
    p = 1 - pow(1-c,1/n) #the probability of being a slot leader for a validator
    m = int(alpha * n)
    b = binom(m,p)
    sum = 0
    for k in range(1,m+1):
        sum = sum + b.pmf(k)
    return pow(1-c, 1-alpha) * sum
    
#finds the probability of only honest validators are selected
def prMulH(c, alpha):
    p = 1 - pow(1-c,1/n) #the probability of being a slot leader for a validator
    m = int(alpha * n)
    b = binom(m,p)
    sum = 0
    for k in range(2,m+1):
        sum = sum + b.pmf(k)
    return pow(1-c, 1-alpha) * sum
    

#finds the probabolity that at least one validator is selected
def prh(c, alpha):
    return c - prM(c, alpha)

#finds the probability that only malicious validators are seleceted
def prM(c, alpha):
    p = 1 - pow(1-c,1/n) #the probability of being a slot leader for a validator
    m = int((1-alpha) * n)
    b = binom(m,p)
    sum = 0
    for k in range(1,m+1):
        sum = sum + b.pmf(k)
    return pow(1-c, alpha) * sum
    
#finds the probability that at least one malicious validator is selected    
def prm(c, alpha):
    return c - prH(c,alpha)
    
def prOneH(c,alpha):
    p = 1 - pow(1-c,1/n) #the probability of being a slot leader for a validator
    return roundtwo(alpha * n * p * pow(1-p, n-1))

def prOne(c,alpha):
    p = 1 - pow(1-c,1/n) #the probability of being a slot leader for a validator
    return roundtwo(n * p * pow(1-p, n-1))
########################### END OF PROBABILITIES ################################


omega = 0.5 #the parameter should be between 0 and 1. 0.5 is the optimum one.
p_attack = 0.005 #the targetted attack probability of BABE

#Checks if the parameters above satisfies the condition of having more only ONE honest validator assigned slot than the others
def checkparams(cx):
    po = prH(cx, alpha) * pow(1-cx, D)
    pOne = prOne(cx,alpha)
    if (po < cx - po):
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
            
c = c_optimize()  #assign a new value if different c value is needed
#c = 0.25
pm = prm(c, alpha)
pM = prM(c, alpha)
pH = prH(c, alpha)
ph = prh(c, alpha)
pOneH = prOneH(c, alpha)  

#The probability of attacking BABE with NTP
def pbabe(s_hcg, s_cq, k, kcq):    
    pcg = prcg(s_hcg,c,omega)
    #print 'pcg is' + str(pcg)
    pcq = precq(kcq)
    #print 'pcq is' + str(pcq)
    pcp = prcp(k,c)
    #print 'pcp is' + str(pcp)
    slots = math.ceil(L/T) # total number of slots in lifetime of Babe
    p = slots/(2 * s_cq +s_hcg) * pow(2,20) * int(n * (1-alpha))* (pcg + pcq + pcp)
    return p


#Finds all the necessary parameters to satisfy the targetted attack probability
def find_params():
    if checkparams(c) == False:
        return "Parameters do not satisfy the condtion p_H (1-c)^D > 0.5"
    p_babe = 1
    R = 0 #epoch length
    kcq = 0
    #it does the steps in https://hackmd.io/yXXiBoWMQe67szJk_PD9sw?both#BABE-with-the-NTP until reaching the target attack probability
    while(p_babe > p_attack and kcq < 10000):
        kcq = kcq+1
        k = 4 * kcq 
        t_hcg = ph * pow(1-c,D) *(1-omega) 
        s_hcg = k / t_hcg
        t = (k-2*kcq)/s_hcg
        s_ecq = kcq / t
        R = math.ceil(2 * s_ecq + s_hcg)
        p_babe = pbabe(s_hcg,s_ecq,k,kcq)
    print '################### PARAMETERS OF BABE WITH NTP ###################'
    print 'c = ' + str(c) + ', slot time T = ' + str(T)
    print 'It is secure in ' + str(int(round(L * 3.16887646 * pow(10,-8),1))) + ' years with probability ' + str(1-p_babe)
    print 'It is resistant to ('+ str(D* T + T) + ' - block generation time) second network delay'
    print '~~~~~~~~~~~~~~ Common Prefix Property ~~~~~~~~~~~~~~'
    print 'k = ' + str(k)
    print 'It means: Prun the last ' + str(k) + ' blocks of the best chain. All the remaining ones are probabilistically finalized'
    print '~~~~~~~~~~~~~~ Epoch Length ~~~~~~~~~~~~~~'
    print 'Epoch length should be at least ' + str(R) + ' slots,' + str(R * T/60.0/60.0)+' hours'
    print p_babe
    
    


############ PROBABILITIES OF BREAKING ONE OF THE SECURITY PROPERTIES OF BABE ############   
def prcg(s_hcg, c, omega): 
    return math.exp(-(ph * pow(1-c, D) * s_hcg * pow(omega,2))/2)

def precq(kcq):
    #k = (1-delta) * s_cq * c 
    #return math.exp(-c * s_cq * pow(delta,2)/2) * k/ 2 * pow(ph * pow(1-c, D),k)
    return math.exp(-kcq)
    
def prcp(k,c):
    return math.exp(-(k ))

  
find_params(

{ pkgs ? import <nixpkgs> {} }:

let

  my-python = pkgs.python3;

  pymdown-extensions = pkgs.callPackage ./pymdown-extensions.nix {

    inherit(pkgs.python3Packages) buildPythonPackage markdown pygments

    pytestCheckHook pyyaml isPy3k;

  };

  python-with-my-packages = my-python.withPackages (p: with p; [

    sphinx

    sphinx-material

    (sphinx-markdown-parser.overrideAttrs(oldAttrs: {

      meta.priority = 10;

    }

      ))

    pymdown-extensions

  ]);

in

pkgs.mkShell {

  buildInputs = [

    python-with-my-packages

  ];

  shellHook = ''

    PYTHONPATH=${python-with-my-packages}/${python-with-my-packages.sitePackages}

    # maybe set more env-vars

  '';

})

    
    
