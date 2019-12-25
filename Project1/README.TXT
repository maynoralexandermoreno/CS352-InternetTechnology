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
