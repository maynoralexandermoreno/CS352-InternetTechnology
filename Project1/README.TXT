Important Notes:  
Runs on python 3  
The program can open and close correcly.  
It can send one (1) packet of data correctly (during the non-dropping and dropping tests).  
It can send up to about 12.4 MB of data without breaking, but it will break at 12.5 MB and above.  
This is an issue because the graders will use about 90MB. Neither we nor the TA's could find the cause, as it does send multiple packets at a smaller scale.
If cause is found, or solution created, I'll throw it into this folder at a later date.

To run the commands are (on seperate computers or terminals)
python3 client1.py -f [testfile to read] -d 127.0.0.1 -u 10001 -v 10000
python3 server1.py -f [file to write the result into] -u 10001 -v 10000  
Pick ports that are not used


Many thanks to my partner Chris Wallace.

ORIGNAL README:  
Welcome to our project 1 submission!

Here I will go over the various functions and our implementation of the project.


init:  
Init simply binds the input from the user to a global variable for use later.  
If none is inputted, it gives a 5555 and 5556 as the ports.


__init__:  
init #2 creates the UDP sockets for sending and receiving information, and binds the receiving socket.  
That way there will be a consistent address to send to.


Bind:  
Bind uh... lets you know this is a server, because only the server1 file actually runs this. It'll be important later


Connect:   
Connect is the client side initiation of the 3 way handshake. It reads the destination port and address from the user and saves it into a touple.  
Our header function uses global variables, that way we don't have to set everything each time if certain variables don't change.  
When it receives a reply, it decodes the header (Based on the model in the assignment) If the reply has the appropriate bytes, it sends an acknowledgement, and continues.


Listen:  
Look, I can read instructions, this is empty


Accept:  
The server side receiving of the 3 way handshake, waits in a loop until it gets a connection, sends its reply, waits for an acknowledgement. Simple stuff


Close:  
Basically just another 3 way handshake, again initiated by the client. Since its the same function that gets called, we broke it up into two parts, separated by whether this instance called "bind" earlier (see, I said it would be important). We had a problem where the client would finish early, and send before the server was ready to receieve, so we just had it take a tiny nap before starting


Send:  
Hoo boy, this is complicated, buckle up. So send first sends the 4 bytes containing the filesize, but after that, it starts to fill 3 buffers (an abstraction of working with window size) The buffers incriment the sequence number, and send one at a time. This sounds disasterous, BUT thanks to a function later, we don't have to worry about packets being dropped. A tricky part to figure out was what to do when the file is smaller than 3 buffer sizes, thus the crazy 3 if statements near the bottom


Recv:   
Less complicated than send. Takes 4 bytes for the filesize and returns it, but then performs is true duty. receiving files comes in 2 flavors, smaller than the defined buffer size, or the same size. The same size one just reads 63000 bytes, and adds it to a huge bytestring (our file) , and sends an acknowledgement. An important thing to note is that the program will not store a buffer to the "file" unless the sequence number in the header is exactly 1 more than the first one it received (starting at 0), if it doesn't get that, it just sends the last ack that it sent over and over until the client gets the picture


BuildHeader:  
This one.... builds a header. Crazy, I know. its a simple struct, following the example in the instructions


GetAcks:  
Okay so, this is how the client receives acknowledgements without putting the whole thing on hold. This modifies a DIFFERENT global sequence number counter, which send uses in case it needs to roll back to the last acknowledged packet.
