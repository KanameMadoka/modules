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


WORDS = ["REGISTER","TOGGLE","TURN", "ON", "OFF", "SWITCH", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN"]
IDS = ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN"]

ONOFF = 0

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
        
    return n & 0xf

def findP(n):
    length = len(bin(n))
    p = 0
    for i in range(0, length):
        p ^= (n >> i) & 0x1
    return p

def turnSwitch(n, s):
    
    myID = getSerial() & 0xf
    
    global ONOFF
    if (s == 1):
        ONOFF = ONOFF |(1 << n)
        output = (myID << 7) | (n << 3) | ON
    else:
        ONOFF = ONOFF & (not(1 << n))
        output = (myID << 7) | (n << 3) | OFF
    print ('onoff {0:b}'.format(ONOFF))
    
    pa = findP(output)
    #output = 0xc << 20 | output << 4 | 0x3 | pa << 19

    print ('output before hamming {0:x}'.format(output))
    output = hamming.encH1511(output)

    output = 0xc << 20 | output << 4 | 0x3 | pa << 19

    ctlSwitch.initial(500)
    count = 2
    while (count > 0):
        ctlSwitch.transmit3(output)
        count = count -1

def toggleSwitch(n):
    global ONOFF
    ONOFF = ONOFF ^ (1 << n)
    
    myID = getSerial() & 0xF
    output = (myID << 7) | (n << 3)
    if (ONOFF & (1 << n)):
        output = output | ON
    else:
        output = output | OFF
    print ('output before hamming = {0:x}'.format(output))
    pa = findP(output)
    print ('pa is {}'.format(pa))
    output = hamming.encH1511(output)
    print ('output after hamming = {0:b}'.format(output))
    output = 0xc << 20 | output << 4 | 0x3 | pa << 19
    print ('final output is {0:x}'.format(output))
    ctlSwitch.initial(500)
    rec = False
    count = 2
    while (not rec and count > 0):
        ctlSwitch.transmit3(output)
        #rec = ctlSwitch.receive(ACK)
        count = count -1

#def process(rec, data, pa, debug = False):
#    return False
#def register():
#    id = receive(cmd = BROAD, timeout = 1)

def handle(text, mic, profile):
    #try:
    print (text)
    f = open('switch.txt', 'r+')
    i = 0
    debug = True
    listName = []
    listID = []
    for line in f:
        if (line == '\n'):
            print ('empty line')
            break
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
    f.close()
    turn = bool(re.search(r'\bturn\b', text, re.IGNORECASE))      
    toggle = bool(re.search(r'\btoggle\b', text, re.IGNORECASE))
    register = bool(re.search(r'\bregister\b', text, re.IGNORECASE))
    print (toggle)
    if (turn):
        for item in listName:
            if (bool(re.search(r'\b'+ item + r'\b', text, re.IGNORECASE))):
                print ('trun true 1')
                ind = listName.index(item)
                if (bool(re.search(r'\bon\b', text, re.IGNORECASE))):
                    print ('turn on switch')
                    turnSwitch(listID[ind], 1)
                elif (bool(re.search(r'\boff\b',text, re.IGNORECASE))):
                    print ('turn off switch')
                    turnSwitch(listID[ind], 0)
    if (toggle):
        for item in listName:
            print (item)
            if (bool(re.search(r'\b'+item+ r'\b', text, re.IGNORECASE))):
                print ('true1')
                ind = listName.index(item)
                toggleSwitch(listID[ind])
                return
        info = "device not exist"
        mic.say(info)
        return
    if (register):
        id = ctlSwitch.receive(cmd = BROAD, timeout = 1)
        if (id == 0):
            info = "please plug in your device and try again"
            print (info)
            mic.say(info)
            return
        for name in IDS:
            if (bool(re.search(r'\b'+name+r'\b', text, re.IGNORECASE))):
                if (name in listName):
                    info = "name " + name +" already in use, please select another one"
                    print (info)
                    mic.say(info)
                    return
                if (id in listID):
                    info = "unexpect error, you may register at most 2 device at time"
                    print (info)
                    mic.say(info)
                listName.append(name)
                listID.append(id)
            
                id = id ^ 1
        f = open("switch.txt", 'w')
        for id, name in zip(listID, listName):
            #f.write(str(id)+'\n')
            f.write(name+'\n')
            f.write(str(id) + '\n')

   # except:
   #     print('no data')
            


def isValid(text):
    """
        Returns True if the input is related to the meaning of life.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\bswitch\b', text, re.IGNORECASE))
