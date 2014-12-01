# -*- coding: utf-8-*-
import random
import re
import hamming
import ctlSwitch


#cmd table
ACK = 7
BROAD = 1
ON = 0
OFF = 3
TOGGLE = 5
UNREG = 6


WORDS = ["TOGGLE","TURN", "ON", "OFF", "SWITCH", "ONE", "TWO"]


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

def findP(n):
    length = len(bin(n))
    p = 0
    for i in range(0, length):
        p ^= (n >> i) & 0x1
    return p

def toggleSwitch(n):
    myID = getSerial() & 0xF
    output = (myID << 7) | (n << 3)
    print ('output before hamming = {0:x}'.format(output))
    pa = findP(output)
    print ('pa is {}'.format(pa))
    output = hamming.encH1511(output)
    print ('output after hamming = {0:b}'.format(output))
    output = 0xc << 20 | output << 4 | 0x3 | pa << 19
    print ('final output is {0:x}'.format(output))
    ctlSwitch.initial(500)
    rec = False
    count = 10
    while (not rec and count > 0):
        ctlSwitch.transmit(output)
        rec = ctlSwitch.receive(ACK)
        count = count -1

#def process(rec, data, pa, debug = False):
#    return False


def handle(text, mic, profile):
    #try:
    print (text)
    f = open('switch.txt', 'rw')
    i = 0
    debug = True
    listName = []
    listID = []
    for line in f:
        line = line.rstrip('\n')
        print (line)
        if (i & 0x1):
            listID.append(int(float(line)))
        else:
            listName.append(line)
        i = i+1
    
    if (debug):
        print (listName)
        print (listID)
      
    toggle = bool(re.search(r'\btoggle\b', text, re.IGNORECASE))
    print (toggle)
    if (toggle):
        for item in listName:
            print (item)
            if (bool(re.search(r'\b'+item+ r'\b', text, re.IGNORECASE))):
                print ('true1')
                ind = listName.index(item)
                toggleSwitch(listID[ind])
   # except:
   #     print('no data')
            


def isValid(text):
    """
        Returns True if the input is related to the meaning of life.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\bswitch\b', text, re.IGNORECASE))
