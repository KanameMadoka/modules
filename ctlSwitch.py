import RPi.GPIO as GPIO
from time import sleep
from time import time
import signal
import math as math
import os, psutil
from hamming import *
import pigpio


#cmd table
ACK = 7
ON = 0
OFF = 3
TOGGLE = 5
BROAD = 1


global Baud 
Baud = 0 
pi1 = pigpio.pi()

def initial(val):
    """GPIO.setmode(GPIO.BCM)"""
    global pi1
    pi1 = pigpio.pi()
    global Baud 
    Baud = val
    pi1.set_mode(18, pigpio.OUTPUT)
    pi1.set_mode(24, pigpio.OUTPUT)
    pi1.set_mode(25, pigpio.OUTPUT)
    pi1.write(18,1)
    pi1.write(24, 1)
    pi1.write(25, 1)

def getSerial():
    cpuserial = "0000000000000000"
    try:
        f = open ('/proc/cpuinfo','r')
        for line in f:
            if line[0:6] == "Serial":
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR00000000000"
    n = 0
    #print ('cpuSrial is')
    #print(cpuserial)
    for c in cpuserial:
        n += int(ord(c))
        
    return n & 0xF

def test():
    initial(500)
    print('baud = {}'.format(Baud))
    receive(debug = True)
    

def sendInfo(n):
    #GPIO.setup(23, GPIO.OUT, pull_up_down = GPIO.PUD_DOWN)
    if (n==0):
        """GPIO.output(23, False)"""
        pi1.write(23, 0)
        #print 0
    else:
        """GPIO.output(23,True)"""
        pi1.write(23, 1)
        #print 1

def testSend():
    startTime = time()
    curTime = time()
    while(True):
        
        bit = int((time() - startTime)*Baud)
        val = bit % 2
        sendInfo(val)
        #print (val)
       
        

def mySleep(n):
    #print ('sleep {}'.format(n))
    startTime = time()
    curTime = time()
    while(startTime + n>curTime):
        curTime = time()
    return curTime - startTime

def mySleep2(n):
    sleep(n)

def transmit4(val):
    for i in range (0, 100):
        transmit(0xf0f0f0f0)
        transmit(val)

def transmit3(val):
    for i in range(0, 50):
        transmit(val)


def transmit2(val):
    for i in range (0,100):
        transmit(0xAAAAA)
    transmit(val)
    for i in range (0, 100):
        transmit(0xAAAAA)


def transmit(val):
    """GPIO.setup(23, GPIO.OUT, pull_up_down = GPIO.PUD_DOWN)"""
    s = signal.signal(signal.SIGINT, signal.SIG_IGN)
    #p = psutil.Process(os.getpid())
    #storedNice = p.nice()
    #print (storedNice)
    #p.nice(31)

    startTime = time()
    curTime = time()
    bit = int((curTime - startTime)*Baud)

    while(bit < 32):
        sendInfo ((val >> bit)&0x1)
        bit = int ((time() - startTime)*Baud)
        #print bit
    #p.nice(storedNice)     
    signal.signal(signal.SIGINT, s)
    #mySleep(0.04)
    #GPIO.cleanup()

def process(cmd, data, pa, debug = False, additionalData = None):
    if (cmd == ACK):
        if (data & 0x7 != ACK):
            return 0
        if ((data >> 7) != getSerial()):
            return 0
        return 1
    if (cmd == BROAD):
        if (data & 0x7 != BROAD):
            return 0
        if ((data >> 7)!= 0xF):
            return 0
        return (data >> 3)& 0xF

    return 0


        
def receive(cmd = 7, timeout = 3.2, debug = False):
    """GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)"""
    buf = 0L
    pi1.write(25, 0)
    pi1.set_mode(23, pigpio.INPUT)
    startTime = time()
    curTime = startTime
    counter = 0
    while (curTime - startTime < timeout ):
        #buf = ((buf << 1) | pi1.read(23) ) &  0xFFFFFF
        """edited here"""
        #delay = mySleep(1.0/Baud)
        curTime = time()
        
        if ((curTime - startTime)*Baud > counter):
            #counter = counter + 1
	    val = (curTime - startTime)*Baud
            counter = int(val)
            if (val - counter > 1):
                print ("esacpe {}".format(val-counter))
        
            buf = ((buf << 1) | pi1.read(23) ) & 0xffffff
        if (counter % 8 == 0):
	    print('buf has = {}'.format(buf))
        
        #if (debug) :
            #print('buf = {0:X}'.format(pi1.read(23)))
        #if (debug):
            #print ('timeout = {}'.format(timeout))
        if ((buf & 0xF0000F) == 0xc00003):
            if (debug):
                print ('11buf = {0:X}'.format(buf))
            pa = (buf >> 19) & 0x1
            trunked = (buf >> 4) & 0x7fff
            dec = decH1511(trunked)
            retVal = process(cmd, dec, pa)
            if (retVal != 0):
                pi1.write(25, 1)
                pi1.set_mode(23, pigpio.OUTPUT)
                return retVal
        elif ( (buf & 0xF00000) == 0xc00000 and (buf & 0x3)!= 0):
            continue
            if (debug):
                print ('corrupted buf = {0:X}'.format(buf))
            pa = (buf >> 19) & 0x1
            trunked = (buf >> 4) & 0x7fff
            dec = decH1511(trunked)
            retVal = process(cmd, dec, pa)
            if (retVal != 0):
                pi1.write(25, 1)
                pi1.set_mode(23, pigpio.OUTPUT)
                return retVal
    if (debug):
        print('receive timeout')
    pi1.write(25, 1)
    return False
        



    
initial(500)    

