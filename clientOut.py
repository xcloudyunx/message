import socket, os, time, getpass, hashlib, sys
from cipher import AESCipher

def SEND(message):
	server.send(cipher.encrypt(message))

def RECV():
	return cipher.decrypt(server.recv(2048))

if len(sys.argv) < 4:
	sys.exit()

cipher = AESCipher("")			#####some random string that is same as server#####
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP_address = "127.0.0.1"	#####change to server ip#####
Port = 5321
server.connect((IP_address, Port))
SEND(hashlib.sha256(RECV()).hexdigest())
if RECV() != "AUTHORISED":
	server.close()
	sys.exit()

SEND("OUTPUT")
os.system("title Output " + sys.argv[2])

SEND(sys.argv[1] + " " + sys.argv[2])
if RECV() != "ACCEPTED":
	server.close()
	sys.exit()
	
key = AESCipher(sys.argv[3])

while True:
	message = RECV()
	if message == "EXIT":
		server.close()
		print "Logged off"
		sys.exit()
	elif message == "DODGE":
		server.close()
		print sys.argv[2] + " has disconnected"
		os.system("pause")
		sys.exit()
	message = key.decrypt(message)
	print message


server.close()