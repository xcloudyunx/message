import socket, os, time, getpass, hashlib, sys
from cipher import AESCipher

def SEND(message):
	server.send(cipher.encrypt(message))
	
def RECV():
	return cipher.decrypt(server.recv(2048))
	
def serverThread():
	while True:
		reply = RECV()
		if reply == "EXIT":
			print "Logged off"
			sys.exit()

if len(sys.argv) < 1:
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

SEND("DISPLAY")
os.system("title Display")

SEND(sys.argv[1])
if RECV() != "ACCEPTED":
	server.close()
	sys.exit()

while True:
	num = RECV()
	if num == "EXIT":
		server.close()
		sys.exit()
	
	num = int(num)
	os.system("cls")
	print "Online:",
	for i in xrange(num):
		print RECV() + ",",
	print RECV()
	
	print "Active connections:",
	num = int(RECV())
	for i in xrange(num):
		print RECV() + ",",
	if num >= 0:
		print RECV()
	else:
		print
	
	print "Pending inbounds:",
	num = int(RECV())
	for i in xrange(num):
		print RECV() + ",",
	if num >= 0:
		print RECV()
	else:
		print
	
	print "Pending outbounds:",
	num = int(RECV())
	for i in xrange(num):
		print RECV() + ",",
	if num >= 0:
		print RECV()
	else:
		print
	
	time.sleep(4)
	

server.close()