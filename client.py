import socket, os, time, getpass, hashlib, threading, sys
from cipher import AESCipher

def SEND(message):
	server.send(cipher.encrypt(message))
	
def RECV():
	return cipher.decrypt(server.recv(2048))

def serverThread():
	while True:
		command = raw_input()
		SEND(command)

cipher = AESCipher("")			#####some random string that is same as server#####
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP_address = "127.0.0.1"	#####change to server ip#####
Port = 5321
server.connect((IP_address, Port))
SEND(hashlib.sha256(RECV()).hexdigest())
if RECV() != "AUTHORISED":
	server.close()
	sys.exit()

SEND("HUB")
os.system("title Hub")

while True:
	_name = raw_input("Name: ")
	SEND(_name)
	
	if RECV() == "NEW":
		password0 = getpass.getpass("Please enter your password: ")
		password1 = getpass.getpass("Please confirm your password: ")
		while password0 != password1:
			print "Passwords do not match."
			password0 = getpass.getpass("Please enter your password: ")
			password1 = getpass.getpass("Please confirm your password: ")
		SEND(password0)
		continue
		
	password = getpass.getpass("Password: ")
	SEND(password)
	auth = RECV()
	if auth == "CORRECT":
		print "Logged in succesfully"
		break
	elif auth == "LOGGED":
		print "User already logged in"
	elif auth == "INCORRECT":
		print "Name or password is incorrect"

os.system("start clientDisplay.py " + _name)	#####remove ".py" if redistributing#####

serv = threading.Thread(target=serverThread)
serv.daemon = True
serv.start()

while True:
	reply = RECV()
	if reply == "HELP":
		print "Help menu that I can't be bothered writing right now"
		
	elif reply == "EXIT":
		server.close()
		print "Logged off"
		sys.exit()
	
	elif reply == "CONNECT SUCCESSFUL":
		print "Request sent successfully"
	elif reply == "CONNECT REPEAT":
		print "Request already sent"
	elif reply == "CONNECT SELF":
		print "Cannot send request to yourself"
	elif reply == "CONNECT UNSUCCESSFUL":
		print "User either not online or doesn't exist"
		
	elif reply == "ACCEPT SUCCESSFUL":
		name = RECV()
		key = RECV()
		print "Connection established with", name
		os.system("start clientIn.py " + _name + " " + name + " " + key)	#####remove ".py" if redistributing#####
		os.system("start clientOut.py " + _name + " " + name + " " + key)	#####remove ".py" if redistributing#####
	elif reply == "ACCEPT UNSUCCESSFUL":
		print "User did not send request"
		
	elif reply == "DISCONNECT SUCCESSFUL":
		print "Disconnect successful"
	elif reply == "DISCONNECT UNSUCCESSFUL":
		print "Not connected to user"
		
	elif reply == "ROOM CONNECT SUCCESSFUL":
		print "Request sent successfully"
	elif reply == "ROOM CONNECT SELF":
		print "Cannot send request to yourself"
	elif reply == "ROOM CONNECT UNSUCCESSFUL":
		print "Users either not online or don't exist"
		
	elif reply == "SHORT":
		print "Please enter valid name(s)"
		
	elif reply == "INVALID":
		print "Command does not exist. For a list of commands type help"

server.close()