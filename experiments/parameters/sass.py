import math

L = 94670777.9 #Life time of BABE in seconds
n = 100.0 #number of validators

alpha = math.sqrt(0.5)
max_alpha = 0.8
f = int(alpha * n)
max_max_attempts = 64
max_attempts = 0
c = 0.5
delta_hvrf = 0.1
eplen = 1000

delta_hslot = 0.5
p_attack = 0.005
T = 6
ph = 0.5001

def prMalSlot(alpha):
    return 1 - alpha

def prPubSlot(alpha):
    return alpha * (1 - alpha)


def prRandSlot(alpha, eplen,nweak):
    f = (1-alpha) * n
    mu_hvrf = (n-f) * c * alpha * max_attempts
    p_weak = (nweak * max_attempts) / (mu_vrf * (1-delta_hvrf) - (eplen-1))
    if p_weak < 0 or p_weak > 0.01:
        return 1
    print('pweak is ' + str(p_weak))
    return (1- math.exp(-mu_hvrf * pow(delta_hvrf,2) /2)) * p_weak

def prHslot(alpha,eplen):
    pm = prMalSlot(alpha)
    pp = prPubSlot(alpha)
    pr = prRandSlot(alpha,  eplen)
    return 1 - pm - pp - pr


def prECQ(k_ecq):
    return math.exp(-k_ecq)

def prCP(k):
    return math.exp(-k)

def prHCG(s_hcg,  eplen):
    ph = 0.51
    e = s_hcg * ph * pow(delta_hslot, 2)/2
    return math.exp(-e)

def pSass(s_hcg, s_ecq, k, k_ecq):   
    eplen = 2 * s_ecq +s_hcg 
    pcg = prHCG(s_hcg,  eplen) + 2 * prECQ(k_ecq)
    pcp = prCP(k)
    #print 'pcp is' + str(pcp)
    slots = math.ceil(L/T) # total number of slots in lifetime of Babe
    p = (slots/eplen) * pow(2,20) * int(n * (1-alpha))* (pcg + pcp)
    return p


def check_pr(eplen):
    mu_vrf = (n-f) * c * alpha * max_attempts
    if (mu_vrf * (1-delta_hvrf) - (eplen-1)) < 0:
        return False
    else: return True

def find_max(eplen,nweak):
    pm = prMalSlot(alpha)
    pp = prPubSlot(alpha)
    pr = 1 - pm - pp - ph
    # print(pr)
    # print((n-f) * c * alpha * (1-
    # delta_hvrf))
    
    if pr < 0:
        return -1
    max_attempts = pr * (eplen - 1) / (pr * (n-f) * c * alpha * (1-delta_hvrf) - nweak)
    return math.ceil(max_attempts)



k = 0
psass = 1
eplen = 100
while(psass > p_attack):
    s_ecq = int(eplen/3)
    s_hcg = eplen - 2 * s_ecq
    t_hcg = ph * (1-delta_hslot) 
    t = t_hcg * s_hcg/ (2 * s_ecq + s_hcg)
    k_ecq = s_ecq * t
    k = eplen * t
    #print('k = ' + str(k) + 'k_ecq = '+str(k_ecq))
    psass = pSass(s_hcg, s_ecq, k, k_ecq)
    eplen = eplen + 1
    #print(psass)

nweak_lst = [1,2,3,4,5,6,7]
print
print('eplen: ' + str(eplen) + ' k: ' + str(k))
for nweak in nweak_lst:    
    counter = 0
    alpha = math.sqrt(0.5)
    c = 0.5
    max_attempts = find_max(eplen,nweak)
    while max_attempts < 0 or max_attempts > 64:
    
        if counter % 10 == 0 and alpha < max_alpha :
            alpha = alpha + 0.01
            f = int((1- alpha) * n)
        elif alpha > max_alpha or c < 1:
            c = c + 0.01
        else:
            print('not available')
            break
        counter = counter + 1
        max_attempts = find_max(eplen,nweak)
    print(str(nweak) + '&' + str(round(alpha,2)) + '&' + str(max_attempts) + '&' + str(round(c,2)))
    
    #mu_hvrf = (n-f) * c * alpha * max_attempts
    #print((1- math.exp(-mu_hvrf * pow(delta_hvrf,2) /2)))
    print(r'\\\hline')
