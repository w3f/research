import math
import time
import hashlib
import numpy as np
import matplotlib.pyplot as plt


##### NOTES IN GENERAL ######
# alpha (honest stake), gamma (honest and sync stake), c (prob of non-empty slot), k (probabilistic finality) are as in the description of BABE 
# D is Delta in the description of BABE. D is the maximum delay in terms of SLOT
# Dmax is the maximum resistance in terms of SECOND



Lsec = 31536000/2 #Life time of BABE in seconds
r = pow(2,20)

#precomputed c values for each maximum delay D (in terms of slot) value 
cval = [0.2789, 0.2789, 0.0346, 0.0184, 0.0125, 0.0094, 0.0076, 0.0063, 0.0055, 0.0048, 0.0042, 0.0038, 0.0035, 0.0032, 0.0029, 0.0027, 0.0025, 0.0024, 0.0022, 0.0021, 0.002, 0.0019, 0.0018, 0.0017, 0.0016, 0.0016, 0.0015, 0.0015, 0.0014, 0.0013, 0.0013, 0.0013, 0.0012, 0.0012, 0.0011, 0.0011, 0.0011, 0.001, 0.001, 0.001, 0.001, 0.0009, 0.0009, 0.0009, 0.0009, 0.0008, 0.0008, 0.0008, 0.0008, 0.0008]

#It finds the probability of breaking BABE in 2.5 years.
#The computation is from Theorem 4
#T: slot time, Dmax:maximum delay resistance (seconds), other inputs are as in Theorem 4
def pbabe(T, c, k, gamma, alpha,Dmax):
    beta = 1 - gamma
    D = delta(Dmax,T)
    if D == 0:
        D = 1
    lambda_ = pow(1-c,D)
    stake = lambda_ * alpha *(gamma + lambda_ * beta) 
    L = Lsec/T 
    s = (12*k)/c
    p = r * D  * c * stake * L  * math.exp(-(s * c* stake)/ (16 * D))
    return p

#It finds the minimum k value which makes BABE secure
def mink(T, c, gamma, alpha,D):
    for k in range(100000):
        if pbabe(T, c, k, gamma, alpha,D) <0.01:
            return k

#It finds the minimum epoch length in hours
def epochlen(T, gamma, alpha,Dmax):
    D = delta(Dmax,T)
    c = maxC(T,Dmax,alpha,gamma)
    k = mink(T, c, gamma, alpha,D)
    print D,k,c
    s = (12 * k) / c
    return hour(2*s,T)
    

#Converts e number of slots given T into hour
def hour(e,T):
    ssec = e * T
    smin = ssec/60
    shour = smin/60
    return shour


#Finds the minimum gamma value to satisfy the condition in Lemma 1
#given c, D and alpha
def minG(c,D,alpha):
    for i in range(0,20):
        gamma = i * 0.05
        if D == 0:
            stakeh =  phi(c,alpha*gamma) * pow(1-c,1-alpha) / c
        else:
            stakeh = phi(c,alpha*gamma) * pow(1-c,1-alpha) / c * pow(1-c,D-1)
        
        if stakeh > 0.5:
            return gamma
    return 1
#Finds the minimum gamma value to satisfy the condition in Theorem 4
#given c, D and gamma
def minA(c,D,gamma):
    
    for i in range(0,20):
        alpha = i * 0.05
        if D == 0:
            stakeh =  phi(c,alpha*gamma) * pow(1-c,1-alpha) / c
        else:
            stakeh = phi(c,alpha*gamma) * pow(1-c,1-alpha) / c * pow(1-c,D-1)
        
        if stakeh > 0.5:
            return alpha

#Finds the maximum c value to be resistant to maximum delay Dmax in terms of second
def maxC(T,Dmax,alpha,gamma):
    D = delta(Dmax,T)
    for i in range(10000,1,-1):
        c = i * 0.0001
        stakeh = 0
        if D == 0:
            stakeh =  phi(c,alpha*gamma) * pow(1-c,1-alpha) / c
        else:
            stakeh = phi(c,alpha*gamma) * pow(1-c,1-alpha) / c * pow(1-c,D-1)
        if stakeh > 0.5:
            return float("{:.5f}".format(c))
    return 0

#Finds the maximum c value to be resistant to maximum delay D in terms of slot
def maxCwithD(D,alpha,gamma):
    for i in range(10000,1,-1):
        c = i * 0.0001
        stakeh = 0
        if D == 0:
            stakeh =  phi(c,alpha*gamma) * pow(1-c,1-alpha) / c
        else:
            stakeh = phi(c,alpha*gamma) * pow(1-c,1-alpha) / c * pow(1-c,D-1)
        if stakeh > 0.5:
            return float("{:.5f}".format(c))
    return 0

#Converts delay (Dmax) in seconds to delay in terms of slot given slot time T
def delta(Dmax,T):
    return int(Dmax/T)
        

#Finds the average block time when alpha of the validators are honestly behave
#alpha and gamma needs to be chosen according normal process of BABE (e.g. alpha = 1, gamma = 0.8)
#because we want to find the average blocktime not block time when there is an attack

def blocktime(gamma,alpha,T,Dmax, Davg):
    D = delta(Dmax,T) #maximum delay resistance
    c = 0
    #finds c according to the maximum delay resistance
    if D > len(cval)-1: # if c value is not precomputed for D
        c = maxCwithD(D,0.65,0.8)
        if c == 0:
            return 10000
    else:
        #choose c from precomputed values
        c = cval[D]   
    D = delta(Davg,T) #average network delay 
    L = Lsec/T
    p = condition(c,alpha, gamma,D) # probability of an honest block is added
    return float("{:.3f}".format(L*T /(p*L * c)))



#Finds the probability of being selected with the stake a
def phi(c,a):
    return 1 - pow(1-c,a)

#Probability of honest sync or unscync parties' blocks are added
def condition(c,alpha, gamma,D):
    beta = 1- gamma
    ps = phi(c,alpha*gamma) * pow(1-c,1-alpha) / c * pow(1-c,D-1)
    #print 'ps = '+str(ps)
    pl=  phi(c,alpha*beta) * pow(1-c, 1-alpha * beta)/c * pow(1-c, 2*D-1)
    if D == 0:
        ps = phi(c,alpha*gamma) * pow(1-c,1-alpha) / c
        pl=  phi(c,alpha*beta) * pow(1-c, 1-alpha * beta)/c
    #print 'pl = '+str(pl)
    return ps + pl


#Fiven maximum delay in terms of second, it returns a list of
#minimum slot times for each maximum delay in terms of slot 
def minT(Dmax):
    time = []
    for D in range(0,20):
        if D == 0:
            minT = Dmax + 0.01
            time.append(float("{:.3f}".format(minT)))
            isMin = True
        else:
            minT = float(Dmax/D)
            isMin = False
        while(isMin == False):
            cand = minT - 0.01
            if cand == 0:
                time.append(float("{:.3f}".format(minT)))
                isMin = True
            elif math.floor(Dmax/cand) == D:
                minT = cand
            else:
                time.append(float("{:.3f}".format(minT)))
                isMin = True
    return time


#Finds the best slot time for a given block time (btime)
def findT(alpha,gamma,btime,Dmax,Davg):
    diff = []
    tval = np.arange(0.05,5,0.001)
    bfun = np.vectorize(blocktime)
    bval = bfun(gamma,1,tval,Dmax,Davg)
    #print bval
    minDiff = abs(btime-bval[0])
    minT = tval[0]
    for i in range(len(bval)):
        diff = float("{:.3f}".format(abs(btime-bval[i])))
        if diff == 0:
            return float("{:.3f}".format(tval[i]))
        elif diff < minDiff:
            minDiff = diff
            minT = tval[i]

    if minDiff > 1:
        return 0
            
    return float("{:.3f}".format(minT))


##### Related to Plotting #####

def tval(alpha,gamma,Davg):
    bval = np.arange(4,22,2)
    tfun = np.vectorize(findT)
    tval1 = tfun(alpha,gamma,bval,1,Davg)
    tval2 = tfun(alpha,gamma,bval,2,Davg)
    tval3 = tfun(alpha,gamma,bval,3,Davg)
    tval4 = tfun(alpha,gamma,bval,4,Davg)
    tval5 = tfun(alpha,gamma,bval,5,Davg)
    tval6 = tfun(alpha,gamma,bval,6,Davg)
    tval = [tval1,tval2,tval3,tval4,tval5,tval6]
    return tval, bval

#It plots six graphs where each corresponds a different maximum delay resistance in terms of seconds
def plotBtime(tval,bval):
    
    fig = plt.figure()
    
    ax1 = fig.add_subplot(321)
    ax2 = fig.add_subplot(322)
    ax3 = fig.add_subplot(323)
    ax4 = fig.add_subplot(324)
    ax5 = fig.add_subplot(325)
    ax6 = fig.add_subplot(326)
    
    ax1.set_xticks(bval)
    ax2.set_xticks(bval)
    ax3.set_xticks(bval)
    ax4.set_xticks(bval)
    ax5.set_xticks(bval)
    ax6.set_xticks(bval)
    
 

    ax1.set_title('D = 1 sec')
    ax2.set_title('D = 3 sec')
    ax3.set_title('D = 3 sec')
    ax4.set_title('D = 4 sec')
    ax5.set_title('D = 5 sec')
    ax6.set_title('D = 6 sec')
    

    ax1.set_ylabel('T')
    ax3.set_ylabel('T')
    ax3.set_ylabel('T')
    ax4.set_ylabel('T')
    ax5.set_ylabel('T')
    ax6.set_ylabel('T')

    ax5.set_xlabel('block time')
    ax6.set_xlabel('block time')
    
    ax1.plot(bval,tval[0],'ro', markersize=8)
    ax2.plot(bval,tval[1],'go', markersize=8)
    ax3.plot(bval,tval[2],'bo', markersize=8)
    ax4.plot(bval,tval[3],'yo', markersize=8)
    ax5.plot(bval,tval[4],'bd', markersize=8)
    ax6.plot(bval,tval[5],'rd', markersize=8)

    
    ax1.grid()
    ax2.grid()
    ax3.grid()
    ax4.grid()
    ax5.grid()
    ax6.grid()
    
    plt.show()

def union(lst):
    union = set([])
    for i in range(len(lst)):
        union = set(lst[i]) | union
    return list(union)

def divAxis(lst, distance):
    newlst = []
    last = lst[0]
    i = 1
    newlst.append(float("{:.3f}".format(last)))
    while(i < len(lst)):
        if lst[i] - last >= distance:
            last = lst[i]
            newlst.append(float("{:.3f}".format(last)))
        i = i + 1
    return newlst


 
    
    

                

