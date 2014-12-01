import RPi.GPIO as GPIO
from time import sleep
from time import time
import signal
import math as math
import os, psutil
from hamming import *


#cmd table
ACK = 7
ON = 0
OFF = 3
TOGGLE = 5
BROAD = 1


global Baud 
Baud = 0 

def initial(val):
    GPIO.setmode(GPIO.BCM)
    global Baud 
    Baud = val

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
    print ('cpuSrial is')
    print(cpuserial)
    for c in cpuserial:
        n += int(ord(c))
        
    return n

def test():
    initial(500)
    print('baud = {}'.format(Baud))
    receive(debug = True)
    

def sendInfo(n):
    #GPIO.setup(23, GPIO.OUT, pull_up_down = GPIO.PUD_DOWN)
    if (n==0):
        GPIO.output(23, False)
        #print 0
    else:
        GPIO.output(23,True)
        #print 1

def mySleep(n):
    #print ('sleep {}'.format(n))
    startTime = time()
    curTime = time()
    while(startTime + n>curTime):
        curTime = time()
    return curTime - startTime

def mySleep2(n):
    sleep(n)

def transmit(val):
    GPIO.setup(23, GPIO.OUT, pull_up_down = GPIO.PUD_DOWN)
    s = signal.signal(signal.SIGINT, signal.SIG_IGN)
    p = psutil.Process(os.getpid())
    storedNice = p.nice()
    #print (storedNice)
    p.nice(31)

    startTime = time()
    curTime = time()
    bit = int((curTime - startTime)*Baud)

    while(bit < 32):
        sendInfo ((val >> bit)&0x1)
        bit = int ((time() - startTime)*Baud)
        #print bit
    p.nice(storedNice)     
    signal.signal(signal.SIGINT, s)
    #mySleep(0.04)
    #GPIO.cleanup()

def process(cmd, data, pa, debug = False):
    return False
        
def receive(cmd = 7, timeout = 0.5, debug = False):
    GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    buf = 0L
    while (timeout > 0 ):
        buf = (buf < 1) | GPIO.input(23)
        delay = mySleep(1.0/Baud)
        timeout = timeout - delay
        #if (debug):
            #print ('timeout = {}'.format(timeout))
        if ((buf & 0xc00003) == 0xc00003):
            pa = (buf >> 19) & 0x1
            trucked = (buf >> 4) & 0x7fff
            dec = decH1511(trunced)
            if (process(cmd, dec, pa)):
                return True
        elif ( (buf & 0xc00000) == 0xc00000 and (buf & 0x3)!= 0):
            pa = (buf >> 19) & 0x1
            trunked = (buf >> 4) & 0x7fff
            dec = decH1511(trunked)
            if (process(dec, pa)):
                return True
    if (debug):
        print('receive timeout')
    return False
        
    
    

#GPIO.cleanup()
