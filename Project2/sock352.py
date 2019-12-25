
import binascii
import socket as syssock
import struct
import sys
import random
import signal
import time
import _thread
import threading
import collections

# Global Socket Variables/ Constants
targetDest = None
sock352PktHdrData = '!BBBBHHLLQQLL'
custom_buffer_size = 63000
big_buffer_size = 252000
sizeSent = False
isServer = False
sendSocket = None
recvSocket = None
endThread = False
killRecvThread = False
enoughSpace = True
myfilesize = 0
mySeq = 0   
firstSend = True
lastPacket = False
totalSize = 0

#DA BOOOFER
bigBuffer = collections.deque([])
								
# Global Header Varaibles
version = 0x01
flags = 0x01 # For initial SYN
opt_ptr = 0
protocol = 0
header_len = 0
checksum = 0
source_port = 0
dest_port = 0
sequence_no = 0
ack_no = 0
window = 0
payload_len = 0
lastAcked = -1

# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from


def init(UDPportTx,UDPportRx):   # initialize your UDP socket here 
	### Take in the port numbers as strings, interpret them as integers, save them into global variables
        global portTx
        global portRx
        global sizeSent
        
        
	### Take in transmission, receiving port numbers. Transmission means the port we are shooting info at
        if (UDPportTx == ''):
                portTx  = 5555
        else:
                portTx = int(UDPportTx)
        if (UDPportRx == ''):
                portRx = 5556
        else:
                portRx = int(UDPportRx)
        
        ### No more edits here
 
class socket:
        
                def __init__(self):  # fill in your code here 
                        ### Enable sending and receiving

                        global sendSocket
                        global recvSocket
                       
                        ### Create the sockets, one to send and one to receive packets of information
                        sendSocket = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
                        recvSocket = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
                       
                        ### Bind the receiving socket to to the receinving port 
                        recvSocket.bind(('', portRx))
                        
                        ### Confirm socket initialized
                        print('Sock352 Initialization Complete')
                        return
               
                        ### No more edits here
               
                def bind(self,address):

                        ### Designates a server distinction; Perhaps for future use
                        global isServer
                        isServer = True
                        print('Bind Complete')
                        return

                        ### No more edits here

                def connect(self,address):  # fill in your code here 
                        ### Establish the Three-Way Handshake; Client only method
                        global targetDest, flags, header_len, sequence_no, ack_no, payload_len, received

                        ### Target destination creates an address using the given address, and the port number require to send to 
                        targetDest = (address[0], portTx)
                        
                        ### Create a random sequence number & create a header length
                        sequence_no = random.randint(1, 120)
                        header_len = struct.calcsize(sock352PktHdrData)

                        # print('sequence number is:', sequence_no)
                        # print('header length is: ',header_len)
                        # print('target destination is: ', targetDest)
                
                        ### Call healper meathod to build a Header to send
                        handshakeInitiate = self.buildHeader()
                        
                        recvSocket.settimeout(0.2)
                        
                        received = False
                        while not received:
                                try:
                                        ### First Handshake; Send a packet to the server
                                        sendSocket.sendto(handshakeInitiate, targetDest)

                                        ### Second Handshake; Receive a packet from the server
                                        reply = recvSocket.recv(header_len)

                                        ### Unpack data; uReply[1] is the flag, uReply[9] is the ack__no
                                        uReply = struct.unpack(sock352PktHdrData, reply)

                                        ### The expected response is 1 for the flag, sequence_no + 1 for the ack_no
                                        if(uReply[1] == 1 and uReply[9] == sequence_no +1):
                                                ### If it is the correct information sent back, set the ack_no to be the sequence_no sent by server, and flags
                                                ### Set the new sequence_no to be 0
                                
                                                ack_no = uReply[8]
                                                flags = 0x4
                                                sequence_no = 0
                                
                                                ### Create a new header
                                                handshakeSecondPass = self.buildHeader()
                                
                                                ### Send the third handshake
                                                sendSocket.sendto(handshakeSecondPass, targetDest)#Send Third Handshake
                                                _thread.start_new_thread(self.getAcks,())
                                                #print('My target destination is', targetDest)
                                                received = True
                                                break
                                        else:
                                                ### Didn't get the correct message, trying again
                                                pass
                                except syssock.timeout as e:
                                        err = e.args[0]
                                        if err == 'timed out':
                                                continue
                        return
                        ### No more edits here

                def listen(self,backlog):
                        ### Currently not needed; No more edits here
                        return

                def accept(self):
                        ### Used to accept the Three Way Handshake; Server only
                        global targetDest, flags, header_len, source_no, destination_no, sequence_no, ack_no, payload_len

                        recvSocket.settimeout(0.2)
                        ### Loop to get the first receive packet correctly
                        incoming = False
                        while(incoming == False):
                                try:
                                        ### Use to receive packet and address from client; no data attached
                                        incomingPacket, incomingAddress = recvSocket.recvfrom(struct.calcsize('!BBBBHHLLQQLL'))

                                        ### Use to set the destination location of the client
                                        newDest = (incomingAddress[0], portTx) 
                                        #print('the package comes from address', incomingAddress[0], incomingAddress[1])
                                        targetDest = newDest
                                
                                        ### Unpack the header sent to server; header needs to be 01 to break the while loop
                                        incomingHeader = struct.unpack('!BBBBHHLLQQLL', incomingPacket)
                                        if(incomingHeader[1] == 0x1):
                                                ### If true, set all flags appropriately
                                                flags = 0x1
                                                ### Send back a random header
                                                sequence_no = random.randint(121,200)
                                                ### Ack should be client's sequence_no + 1
                                                ack_no = int(incomingHeader[8]) + 1
                                                payload_len = 0
                                                header_len = struct.calcsize('!BBBBHHLLQQLL')
                                        
                                                ### Build handshake and send the 2nd Handshake to the client
                                                handshakeReply = self.buildHeader()
                                                sendSocket.sendto(handshakeReply, newDest)
                                                #print('my target destination is', targetDest)
                                                incoming = True
                                                break
                                        else:
                                                ### Placeholder for the try except 
                                                continue
                                except syssock.timeout as e:
                                        err = e.args[0]
                                        if err == 'timed out':
                                                continue
                        incoming = False
                        
                        while(incoming == False):
                                try:
                                        ### When done, accept the response for the last handshake; Vital to free recv!!!
                                        incomingPacket, incomingAddress = recvSocket.recvfrom(struct.calcsize('!BBBBHHLLQQLL'))
                                        print('Handshake Connection Accepted!')
                                        incoming = True
                                        _thread.start_new_thread(self.serverPacketStuff,())
                                        ##_thread.start_new_thread(self.serverPacketStuff,())
                                        return (self,incomingAddress)
                                 
                                except syssock.timeout as e:
                                        err = e.args[0]
                                        if err == 'timed out':
                                                continue
                        ### No more edits here

                                
                def close(self):   # Fill your code here
                        
                        global targetDest, flags, header_len, sequence_no, ack_no, payload_len, killRecvThread
                        
                        ### When the server calls close, it will wait for a FIN header
                        if (isServer == True):
                                #killRecvThread = True
                                recvSocket.settimeout(None)
                                receiveFIN = recvSocket.recv(header_len)

                                ### Unpack data; uReply[1] is the flag, uReply[9] is the ack__no
                                finHeader = struct.unpack(sock352PktHdrData, receiveFIN)

                                ### The expected response is 2 for the flag, return sequence_no + 1 for the ack_no
                                if(finHeader[1] == 0x2):
                                        print('Confirming  Close.')
                                        flags = 0x6 # Fin + Ack
                                        ack_no = int(finHeader[8]) + 1
                                        
                                        returnHeader = self.buildHeader()
                                        sendSocket.sendto(returnHeader, targetDest)
                                        print(returnHeader[1])
                                        receiveACK = recvSocket.recv(header_len)

                                        ackHeader = struct.unpack(sock352PktHdrData, receiveACK)
                                        
                                        if(ackHeader[1] == 0x4):
                                              print('Server Closed')
                                              sendSocket.close()
                                              recvSocket.close()
                                              return

                        else:
                                time.sleep(.1)
                                recvSocket.settimeout(None)
                                ### Fin Flag is 0x2. Send it
                                flags = 0x2
                                closeHandshake = self.buildHeader()
                                
                                print('Commencing Close.')

                                ### First Handshake; Send a packet to the server
                                sendSocket.sendto(closeHandshake, targetDest)

                                ### Second Handshake; Receive a packet from the server
                                receiveFINACK = recvSocket.recv(header_len)

                                ### Unpack data; uReply[1] is the flag, uReply[9] is the ack__no
                                finackHeader = struct.unpack(sock352PktHdrData, receiveFINACK)

                                ### THe expected response is 1 for the flag, sequence_no + 1 for the ack_no
                                print("I got the packet")
                                print(finackHeader[1])
                                while(finackHeader[1] != 6):
                                        receiveFINACK = recvSocket.recv(header_len)
                                        finackHeader = struct.unpack(sock352PktHdrData, receiveFINACK)
                                if(finackHeader[1] == 6):
                                ### If it is the correct information sent back, set the ack_no to be the sequence_no sent by server, and flags
                                ### Set the new sequence_no to be 0
                                
                                        ack_no = finackHeader[8]
                                        flags = 0x4
                                        sequence_no = 0
                                
                                        ### Create a new header
                                        ackHeader = self.buildHeader()
                                
                                        ### Send the third handshake
                                        print('Finalizing Close')
                                        sendSocket.sendto(ackHeader, targetDest)#Send Third Handshake
                                        
                                        sendSocket.close()
                                        recvSocket.close()
                                        
                                        return
                                else:
                                        pass
                                        





                                 
                def send(self, buffer):
                        global targetDest, allFragmentsSent, flags, header_len, sequence_no, ack_no, payload_len, recvSocket, sendSocket, window, targetDest, enoughSpace, mySeq, myfilesize, firstSend, lastPacket, totalSize
                        allFragmentsSent = False
                        print("Starting Send....")
                        #print(sequence_no)
                        lastPacket = False
                        start = 0 + (custom_buffer_size* sequence_no)
                        bytessent = 0
                        payload_len = 0
                        myfilesize = len(buffer)
                        print(start)
                        print(myfilesize)
                        #print(buffer)
                        while(allFragmentsSent == False):
                                start = 0 + (custom_buffer_size* sequence_no)
                                ##print(sequence_no)
                                if(myfilesize == 0):
                                        allFragmentsSent = True
                                        continue
                                if(enoughSpace != True):
                                        continue
                                #mySeq = sequence_no
                                if(myfilesize < 63000):
                                        bufferFragment = buffer[start:start+myfilesize]
                                        payload_len = len(bufferFragment)
                                        flags = 0xF
                                        if(firstSend == False):
                                                  lastPacket = True
                                        #("Size is" ,len(bufferFragment))
                                        #time.sleep(.1)
                                else:
                                        flags = 0x1
                                        bufferFragment = buffer[start:start + 63000]
                                        payload_len = len(bufferFragment)
                                if(bufferFragment == []):
                                        allFragmentsSent = True
                                        lastPacket = True
                                        break
                                try:
                                        if(myfilesize > 0):
                                                packetHeader = self.buildHeader()
                                                bytessent += self.sendData(packetHeader, bufferFragment, targetDest)
                                                print(bytessent)
                                                time.sleep(.1)
                                                #bytessent -= 40
                                except syssock.timeout as e:
                                        if e.args[0] == 'timed out':
                                                #print('I timed out')
                                                continue
                        print(bytessent)
                        totalSize -=2
                        return totalSize
                                               
                        
                        
                def recv(self, size):#This is ESSTENTIALLY all that Recv needs to do?
                        global sizeSent, targetDest, flags, header_len, sequence_no, ack_no, payload_len, recvSocket, window, bigBuffer
                        myBytes = []
                        i = 0
                        while(len(bigBuffer) == 0):
                                time.sleep(.1)
                                continue
                        #empty = True
                        #while(empty == True):
                        #        if(len(bigBuffer) == 0):
                        #                #print("Buffer is empty, waiting for more data")
                        #                time.sleep(.1)
                        #                continue
                        #        else:
                        #                empty = False
                        if(len(bigBuffer)<size):
                                print("Requesting more bytes than exist in the buffer")
                                size = len(bigBuffer)
                                print("SIZE IS skdlfjgksldhglksdhglskdjhlksfdg")
                                print(size)
                        while(i<size):
                                myBytes.append(bigBuffer.popleft())
                                i+=1
                                window = big_buffer_size - len(bigBuffer)
                                ackPack = self.buildHeader()
                                sendSocket.sendto(ackPack, targetDest)
                        #if(len(myBytes) == 4):
                         #       print("ENCODING")
                          #      print(myBytes)
                           #     myString = bytes(myBytes)
                            #    ##realBytes = myString.encode('ASCII')
                             #   print(myString)
                              #  return myString
                        reply = bytes(myBytes)
                        return reply
######################
#####################
######################							VERY IMPORTANT PLS READ:
#######################
###################### 
#so for this to work the way I want it to, we need to actually use the "payload length" feature of our header, which will be as simple as setting the variable to len(buffer) in send. This way, we can just have it listen for headers, then know to read that much before stopping               
                def serverPacketStuff(self):
                        global targetDest, flags, header_len, sequence_no, ack_no, payload_len, recvSocket, window, bigBuffer, killRecvThread
                        desiredSeq = 0
                        sequence_no = 0
                        firstPacket = 0
                        totalFile = 9999999
                        print("Thread Started dkfjghldksjfghlskdjfg")
                        while(killRecvThread == False):
                                if(len(bigBuffer)+63000 > big_buffer_size):
                                        window = big_buffer_size - len(bigBuffer)
                                        sendSocket.sendto(ackPack, targetDest)
                                ##print("BREAKS HERE")
                                desiredSeq = sequence_no                                
                                incomingPacket = recvSocket.recv(40)
                                headerData = incomingPacket#[0:header_len]
                                realHeader = struct.unpack(sock352PktHdrData, headerData)
                                incPayload = realHeader[11]
                                print("Payload is", incPayload)
                                print("BigBuffer Has:", len(bigBuffer))
                                print("We want From header:", sequence_no)
                                print("From Header", realHeader[8])
                                if(incPayload > big_buffer_size - len(bigBuffer)):
                                        print("ITS TOO BIG CAP'N, THE BOOFER CAN'T TAKE A HIT LIKE THAT")
                                incomingBytes = recvSocket.recv(incPayload+40)
                                #incPayload = 0
                                #print(incomingBytes)
                                if(realHeader[8] == desiredSeq):
                                        print("correct sequence number")
                                        #if(firstPacket == True and len(incomingBytes) == 4)
                                        #print(incPayload)					        
                                        bigBuffer.extend(incomingBytes[40:])
                                        totalFile -= incPayload
                                        print(totalFile)
                                        if(totalFile == 0):
                                                killRecvThread = True
                                        #print(incomingBytes)
                                        ack_no = realHeader[8] + 1 #Letting the client know we got it
                                        window = big_buffer_size - len(bigBuffer)
                                        payload_len = incPayload
                                        ackPack = self.buildHeader()
                                        sendSocket.sendto(ackPack, targetDest)
                                        if(realHeader[1] == 0xF and realHeader[11] != 4):
                                                print("I'm dead")
                                                killRecvThread = True
                                        if(firstPacket < 1):
                                                print("Got the first packet")
                                                
                                                #time.sleep(.1)
                                        
                                        
                                        else:
                                                sequence_no += 1
                                        firstPacket += 1
                                        
                                elif(realHeader[8] == desiredSeq-1):
                                        ack_no = realHeader[8] + 1 #Letting the client know we got it
                                        window = big_buffer_size - len(bigBuffer)
                                        ackPack = self.buildHeader()
                                        sendSocket.sendto(ackPack, targetDest)
                                        print("Getting old packet")
                                else:
                                        print("Wrong packet")
                                        continue
                        return 
                        
                def addToBuffer(self, bytes):
                        global bigBuffer
                        bigBuffer.extend(bytes)                        
                        return
                        
                        

                        
                
                def buildHeader(self):
                        header = struct.Struct(sock352PktHdrData)
                        ### added window size variable
                        return header.pack(0x1, flags, 0x0, 0x0, header_len, 0x0, 0x0, 0x0, sequence_no, ack_no, window, payload_len)
                
                def sendData(self,header,dataFragment,target):
                        if dataFragment == []:
                                return 0
                        else:
                                #print(header+dataFragment)
                                return sendSocket.sendto(header+dataFragment,target)
                        
                def getAcks(self):
                        global ack_no, recvSocket, sequence_no, header_len, endThread, mySeq, window, enoughSpace, mySeq, payload_len, myfilesize, firstSend, lastPacket, totalSize
                        while(endThread == False):
                                ourSeq = sequence_no
                                try:
                                        incomingAck, incomingAddress = recvSocket.recvfrom(header_len)
                                        ackHeader = struct.unpack('!BBBBHHLLQQLL', incomingAck)
                                        #print("Looking For:", ourSeq +1)
                                        #print("What we got:", ackHeader[9])
                                        if (ackHeader[9] == ourSeq+1 and ackHeader[11] == payload_len):
                                                ourSeq = ackHeader[9]
                                                myfilesize -= payload_len
                                                totalSize += payload_len
                                                print("ACK RECEIVED")
                                                if(lastPacket == True):
                                                        print("Finished!")
                                                        endThread = True
                                                        
                                                        #endThread = True
                                                if(firstSend == True):
                                                        time.sleep(.15)
                                                        firstSend = False
                                                else:
                                                        sequence_no += 1
                                                        print("GETACKS SEQUENCE NUMBER IS: ", sequence_no)
                                               ### myfilesize gets dynamically adjusted; so they will both be >= custom_buffer_size or myfilesize will be between 0 and custom_buffer_size, and so will adjust for the final packet
                                        if (ackHeader[10] >= custom_buffer_size or ackHeader[10] >= myfilesize):
                                                enoughSpace = True
                                        else:
                                                enoughSpace = False
                                except syssock.timeout as e:
                                        if e.args[0] == 'timed out':
                                                print('I timed out')
                                                continue
                        print("I'm dead")
                        return
                

#                        global ack_no, recvSocket, sequence_no, header_len, endThread, mySeq
#                        while(endThread == False):
#                                
#                                try:
#                                        incomingAck, incomingAddress = recvSocket.recvfrom(header_len)
#                                        
#                                        #print('Thread started')
#                                        
#                                                
#                                                
#                                                print('Received', sequence_no)
#                                        else:
#                                        	      print('ROLLING IT BACK')
#                                except syssock.timeout as e:
#                                        if e.args[0] == 'timed out':
#                                               # print('I timed out thrtead')
#                                                endThread == True
#                        return
        


































