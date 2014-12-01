

def getP1(n, debug = False):
    p = 0
    for i in range (0,15):
        if ( (not( i & 0x1 ))  and ((n >> i)&0x1)):
            p ^= 1
            if (debug):
                print ('p1 = {} at {}'.format(p, i))
    return p

def getP2(n, debug = False):
    p = 0
    for i in range (0,14):
        if ((not(( i>>1 ) % 2) ) and (( n >> i) & 0x1)):
            p ^= 1
            if (debug):
                print('p2 = {} at {}'.format(p,i))
    return p

def getP4(n,debug = False):
    p = 0
    for i in range (0,12):
        if ( (not ( (i >> 2) & 0x1) )  and ((n >> i ) &0x1)):
            p ^= 1
            if (debug):
                print ('p4 = {} at {}'.format(p,i))
    return p

def getP8(n, debug = False):
    p = 0
    for i in range (0,8):
        if ((n >> i) & 0x1):
            p ^= 1
            if (debug):
                print('p8 = {} at {}'.format(p,i))

    return p

def getP (n, x, debug = False):
    # n is the val to be cal, x is the the hamming bit (2^x)
    p = 0
    for i in range (0, 16-2**x):
        if ( (not ( (i >> x) & 0x1 ) ) and ((n >> i) & 0x1 )):
            p ^= 1
            if (debug):
                print('p{} = {} at {}'.format(x,p,i))
    return p
        

def encH1511(n, debug = False):
    if (len(bin(n))-2 > 11):
        return -1
    n  = (n & 0x7f) | ((n & 0x380) << 1) | ((n & 0x400) << 2)
    if (debug):
        print ('modified n is {0:b}'.format(n))
    """  
    p1 = getP1(n, debug)
    p2 = getP2(n, debug)
    p4 = getP4(n, debug)
    p8 = getP8(n, debug)
    """
    p1 = getP(n, 0, debug)
    p2 = getP(n, 1, debug)
    p4 = getP(n, 2, debug)
    p8 = getP(n, 3, debug)
    n = n | ( p1 << 14 ) | ( p2 << 13 ) | ( p4 << 11) | ( p8 << 7)
    if (debug):
        print ('p1 = {}'.format(p1))
        print ('p2 = {}'.format(p2))
        print ('p4 = {}'.format(p4))
        print ('p8 = {}'.format(p8))

    
    return n

def decH1511(n, debug = False):
    
    
    #p1 = getP1(n, debug)
    #p2 = getP2(n, debug)
    #p4 = getP4(n, debug)
    #p8 = getP8(n, debug)
    
    p1 = getP(n,0,debug)
    p2 = getP(n,1,debug)
    p4 = getP(n,2,debug)
    p8 = getP(n,3,debug)
    errorSum = p1 *1 + p2 *2 +p4 *4 +p8 *8
    if (debug):
        print(' ')
        print ('p1 = {}; p2 = {}; p4 = {}; p8 = {}'.format(p1,p2,p4,p8))
        print ('errorsum = {}'.format(errorSum))
   

    if (errorSum != 0):
        bitShift = 15 - errorSum
        n ^= (0x1 << bitShift)
        if (debug):
            print ('corrected val = {0:b}'.format(n))
    n = (n&0x7f) | ((n & 0x700) >>1) | ((n & 0x1000)>>2)
    return n
    
        



    
    

