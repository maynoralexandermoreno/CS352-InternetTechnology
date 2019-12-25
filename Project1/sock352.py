
import binascii
import socket as syssock
import struct
import sys
import random
import signal
import time
import _thread

# Global Socket Variables/ Constants
targetDest = None
sock352PktHdrData = '!BBBBHHLLQQLL'
custom_buffer_size = 63000 
sizeSent = False
isServer = False
sendSocket = None
recvSocket = None
endThread = False
myfilesize = 0
mySeq = 0     
								
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
                        
                        recvSocket.settimeout(1)
                        
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
                                        return (self,incomingAddress)
                                 
                                except syssock.timeout as e:
                                        err = e.args[0]
                                        if err == 'timed out':
                                                continue
                        ### No more edits here
    
                def close(self):   # Fill your code here
                        
                        global targetDest, flags, header_len, sequence_no, ack_no, payload_len
                        
                        ### When the server calls close, it will wait for a FIN header
                        if (isServer == True):
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
                                        
                                        receiveACK = recvSocket.recv(header_len)

                                        ackHeader = struct.unpack(sock352PktHdrData, receiveACK)
                                        
                                        if(ackHeader[1] == 0x4):
                                              print('Server Closed')
                                              sendSocket.close()
                                              recvSocket.close()
                                              return

                        else:
                                time.sleep(.5)
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

                def send(self,buffer): ### Will send a header with the file sized already packed first, the send the entire file
                        global sizeSent, allFragmentsSent, start, end, bytessent, sequence_no, ack_no, lastAcked, endThread, myfilesize							        
                        ### First we need to send the packed file size
                        if sizeSent == False:

                                longPacker = struct.Struct("!L")
                                input = longPacker.unpack(buffer)
                                myfilesize = input[0]
                                print('hello, input is', input[0])
                                output = longPacker.pack(input[0])
                                
                                bytessent = sendSocket.sendto(output, targetDest)
                                
                                ### Send the filesize header first
                                ##bytessent = sendSocket.sendto(buffer, targetDest)

                                #print('the address I am sending it to is', targetDest)
                                print('Sent file size successfully')

                                ### Now the data will send
                                sizeSent = True
                                return bytessent

                                ### No more edits here
                        else: 
                                ### Send all information as a series of chunks; requires counters for beginning and end of buffer fragment
                                ### To go back N, you just have a starting point in relation to the last successfully received ack (please send me packet ack_no)
                                allFragmentsSent = False
                                sequence_no = 0
                                start = 0 + custom_buffer_size*sequence_no
                                end = custom_buffer_size + custom_buffer_size*sequence_no
                                bytessent = 0 
                                _thread.start_new_thread(self.getAcks,())
                                while (allFragmentsSent == False):
 ## M. Alex Edit:  I think Go Back N being a size of 3 is reasonable. Anything else is just a matter of scalability
                                        ### Make 3 packets ready to send. Note that for clint, only its own sequence number and the ack from server matter
                                        if(sequence_no != mySeq):
                                                print('ROLLING IT BACK!')
                                        sequence_no = mySeq
                                        packetHeader1 = self.buildHeader()
                                        if(myfilesize < 63000):
                                                bufferFragment1 = buffer[start:start+myfilesize]
                                                if(sequence_no > 300):
                                                        exit(0)
                                        else:
                                                bufferFragment1 = buffer[start:end]
                                        
                                        #rint('Test:',sequence_no, ack_no)
                                        sequence_no += 1

                                        packetHeader2 = self.buildHeader()
                                        if(myfilesize < (63000*2) and myfilesize>63000):
                                                bufferFragment2 = buffer[start+custom_buffer_size:start+myfilesize]
                                                if(sequence_no > 300):
                                                        exit(0)
                                        elif(myfilesize <63000):
                                                pass
                                        else:
                                                bufferFragment2 = buffer[start+custom_buffer_size:end+custom_buffer_size]
                                        
                                        sequence_no += 1
                                        packetHeader3 = self.buildHeader()
                                        if(myfilesize < (63000*3)and myfilesize>(63000*2)):
                                                bufferFragment3 = buffer[start+(custom_buffer_size*2):start+myfilesize]
                                                if(sequence_no > 300):
                                                        exit(0)
                                        elif(myfilesize < (63000*2)):
                                                pass
                                        else:
                                                bufferFragment3 = buffer[start+custom_buffer_size*2:end+custom_buffer_size*2]
                                        



                                        #rint('Test:',sequence_no, ack_no)
                                       #print('Test:',sequence_no, ack_no)
                                        #packetHeader2 = self.buildHeader()
                                        #bufferFragment2 = buffer[start+custom_buffer_size:end+custom_buffer_size]
                                        #rint('Test:',sequence_no, ack_no)
                                        
                                       # sequence_no += 1
                                        #packetHeader3 = self.buildHeader()
                                        #bufferFragment3 = buffer[start+custom_buffer_size*2:end+custom_buffer_size*2]
                                       #print('Test:',sequence_no, ack_no)


                                        #print('Buffer 2 fragment size', len(bufferFragment2))
                                        #print('Buffer 1 fragment size', len(bufferFragment1))
                                        #print('Buffer 3 fragment size', len(bufferFragment3))
                                        ### Make 3 buffer fragments ready to send.
                                        ### If start is in bound, but end is out of bound, will create list from start to actual end
                                        ### If both start and end are out of bound, returns []
                                
                                        
                                        
                                        ### hen there is no more information to send
                                        if(bufferFragment1 == [] and bufferFragment2 == [] and bufferFragment3 == []):
                                               allFragmentsSent = True
                                               break
                                        #print('start array at ', start)
                                        #print('end array at', end)

## M. Alex Edits: I do not have a good enough grasp on threads to use em                                       
## You can say that's a...sleepy program HA!
## I would argue that this is fundamentally stop and wait. Send 3 packets at "once" and receive 3 acks. This method should account for the three possible senarios

                                        try:
                                                ### Set the timeout for the recvSocket to adjust for the .01 sleep 
                                                recvSocket.settimeout(.21)
                                                ### Send 3 chunks of data, if there are three chunks of data to send (may be 2 or 1)
                                                if (myfilesize > 0):
                                                		  
                                                        bytessent += self.sendData(packetHeader1,bufferFragment1,targetDest)
                                                        bufferFragment1 = b''
                                                        if(myfilesize>63000):
                                                                myfilesize -= custom_buffer_size
                                                        else:
                                                                myfilesize = 0
                                                        time.sleep(.02)
                                                        print('Bytessent1', bytessent)
                                                else:
                                                        allFragmentsSent = True
                                                        break
                                                if (myfilesize > 0):
                                                        bytessent += self.sendData(packetHeader2,bufferFragment2,targetDest)
                                                        bufferFragment2 = b''
                                                        if(myfilesize>63000):
                                                                myfilesize -= custom_buffer_size
                                                        else:
                                                                myfilesize = 0
                                                        time.sleep(.02)
                                                        print('Bytessent2', bytessent)
                                                else:
                                                        allFragmentsSent = True
                                                        break
                                                if (myfilesize > 0):
                                                        bytessent += self.sendData(packetHeader3,bufferFragment3,targetDest)
                                                        bufferFragment3 = b''
                                                        if(myfilesize>63000):
                                                                myfilesize -= custom_buffer_size
                                                        else:
                                                                myfilesize = 0
                                                        time.sleep(.02)
                                                        print('Bytessent3', bytessent)
                                                else:
                                                        allFragmentsSent = True
                                                        break

                                                ### Receive 3 acks 
                                                ### order is ensured with the if statements, out of order, go back N
                                                ### If there is a timeout, go to except, start again, go back N

## M. Alex: It holds at this recv...again. Seriously, every time I make progress its a goddamn recv call that screws with me!


                                                #incomingAck, incomingAddress = recvSocket.recvfrom(header_len)
                                                #ackHeader = struct.unpack('!BBBBHHLLQQLL', incomingAck)
                                                #if (ackHeader[9] == sequence_no + 1):
                                                #        sequence_no = ackHeader[9]
                                                #        print('Received 2', sequence_no)

                                                #incomingAck, incomingAddress = recvSocket.recvfrom(header_len)
                                                #ackHeader = struct.unpack('!BBBBHHLLQQLL', incomingAck)
                                                #if (ackHeader[9] == sequence_no + 1):
                                                #        sequence_no = ackHeader[9]
                                                #        print('Received 3', sequence_no)
                                        except syssock.timeout as e:
                                                if e.args[0] == 'timed out':
                                                        print('I timed out')
                                                        continue
                                        
                                       # print('BYTES SENT:', bytessent)
                                endThread = True       
                                return bytessent 

## M. Alex Edits: This part only needs to keep trying to receive information. Then, is there a need to have a try except block here? I don't see one. 
                def recv(self,nbytes):
                        ## Server only function that stays on until the socket is closed. Keeps waiting for information to be sent based on # of bytes in file
                        global sizeSent, targetDest, flags, header_len, sequence_no, ack_no, payload_len, recvSocket

                        ### First packet received will be the length of the incoming file. Send immediately to the Server
                        if nbytes == 4:
## M. Alex: Does this part need a while loop? In other words, is this a packet we need to expect to be dropped?
                                #longPacker = struct.Struct('!L')
                                receivedSize, inaddress = recvSocket.recvfrom(4) # for later; may need to send back a confirmation...
                                #input = struct.unpack('!L', inp)
                                #print(inp)
                                #print('received is', input[0])
                                print('the package comes from address', inaddress[0], inaddress[1])
                                #output = longPacker.pack(input[0])
                                print('Received file size successfull')
                                return receivedSize
                        else:
                                ## The file size input is how many bytes that we know we need to receive. This creates a natural canidate for a counter
                                ## data bytes is buffer size + header lenght to be the entire size of packet data
                                bytesleft = nbytes
                                databytes = header_len+custom_buffer_size 
                                ack_no = 0
                                ## bytesreceived is a bytestring that is to be returned to the Server, to be written into a file by the server function
                                bytesreceived = b''
                                while (True):
                                        ## Not being told which packets would be dropped, we assume both client and server packets can be dropped
                                        ## If the client's packet is dropped, they will either not receive an ack (timeout) or receive one out of order
                                        ## That is go back N

                                        ## If the filesize is bigger than the buffer, keep accepting chunks of 63000 + header data until the last chunk
                                        ## Use bytesleft to be a natural counter, decreasing by custom buffer size of 63000

                                        if bytesleft > (custom_buffer_size):#This was a minus. chris just thinks hes clever
                                                print('bytesleft == ', bytesleft)
                                                
                                                ## Wait for the next packet of 63000k size
                                                #i = random.randint(1,5)
                                                ##if(i == 3):
                                                ##        print('DROPPIN THAT SHIT BOIIIIIII')
                                                ##        continue                                                
                                                incomingPacket = recvSocket.recv(databytes) 
                                                headerData = incomingPacket[0:header_len]
                                                realHeader = struct.unpack(sock352PktHdrData, headerData)
                                        
                                                ## Tests to see if the incoming sequence_no == the expected ack_no; if so send new ack, if not send the last ack
                                                if(realHeader[8] == ack_no):
                                                        ack_no += 1
                                                        ## As well, if it is the correct sequence_no, then it is safe to include the data into bytestring
                                                        tempBytes = incomingPacket[header_len:]
                                                        bytesreceived = b''.join([bytesreceived,tempBytes]) # This was a plus equals
                                                        bytesleft -= custom_buffer_size
                                                
                                                ## Either way, send back the header
                                                returnHeader = self.buildHeader()
                                                sendSocket.sendto(returnHeader, targetDest)

                                        else:
                                                ## Single packet and end of multi-packet messages will end here. bytesreceived is returned here. 
                                                #print('bytesleft = ', bytesleft)
                                                print('bytesleft == ', bytesleft)
                                                incomingPacket = recvSocket.recv(bytesleft+40) 
                                                headerData = incomingPacket[0:header_len]
                                                realHeader = struct.unpack(sock352PktHdrData, headerData)
                                                if(realHeader[8] == ack_no):
                                                        ack_no += 1
                                                        tempBytes = incomingPacket[header_len:]
                                                        bytesreceived = b''.join([bytesreceived,tempBytes]) # .join([bytesreceived, tempBytes])
                                                        bytesleft -= custom_buffer_size
                                                        returnHeader = self.buildHeader()
                                                        sendSocket.sendto(returnHeader, targetDest)
                                                        return bytesreceived
                                                else:
                                                        returnHeader = self.buildHeader()
                                                        sendSocket.sendto(returnHeader, targetDest)
                
                def buildHeader(self):
                        header = struct.Struct(sock352PktHdrData)
                        return header.pack(0x1, flags, 0x0, 0x0, header_len, 0x0, 0x0, 0x0, sequence_no, ack_no, 0x0, payload_len)
                
                def sendData(self,header,dataFragment,target):
                        if dataFragment == []:
                                return 0
                        else:
                                return sendSocket.sendto(header+dataFragment,target)
                        
                def getAcks(self):
                        global ack_no, recvSocket, sequence_no, header_len, endThread, mySeq
                        while(endThread == False):
                                
                                try:
                                        incomingAck, incomingAddress = recvSocket.recvfrom(header_len)
                                        ackHeader = struct.unpack('!BBBBHHLLQQLL', incomingAck)
                                        #print('Thread started')
                                        if (ackHeader[9] == mySeq+1):
                                                sequence_no = ackHeader[9]
                                                mySeq += 1
                                                print('Received', sequence_no)
                                        else:
                                        	      print('ROLLING IT BACK')
                                except syssock.timeout as e:
                                        if e.args[0] == 'timed out':
                                               # print('I timed out thrtead')
                                                endThread == True
                        return
        


































