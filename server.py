import socket, sys, hashlib, random, string, time, threading, os
from cipher import AESCipher

def SEND(conn, message):
	conn.send(cipher.encrypt(message))
		
def RECV(conn):
	return cipher.decrypt(conn.recv(2048))

def addUser(name, password):
	names.append(name)
	file = open("names.txt", "a")
	file.write("\n"+name)
	file.close()
	
	passwords.append(password)
	file = open("passwords.txt", "a")
	file.write("\n"+password)
	file.close()
	
	new.remove(name)
	file = open("new.txt", "w")
	for l in new:
		file.write(l+"\n")
	file.close()

def newConnection(conn, addr):
	key = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
	SEND(conn, key)
	if RECV(conn) != hashlib.sha256(key).hexdigest():
		SEND(conn, "FUCK OFF")
		conn.close()
		return
	SEND(conn, "AUTHORISED")
	
	clientType = RECV(conn)
	if clientType == "HUB":
		while True:
			name = RECV(conn)
			
			if name in new:
				SEND(conn, "NEW")
				password = hashlib.sha256(RECV(conn)).hexdigest()
				addUser(name, password)
				continue
				
			SEND(conn, "OLD")
			password = hashlib.sha256(RECV(conn)).hexdigest()
			if name in names:
				if password in passwords:
					if passwords[names.index(name)] == password:
						if name in clients:
							SEND(conn, "LOGGED")
							continue
						SEND(conn, "CORRECT")
						break
			SEND(conn, "INCORRECT")
		
		clients[name] = user(name, conn, addr)
		print "<" + addr[0] + "> " + name + " HUB connected"
		hub = threading.Thread(target=clients[name].HUB)
		hub.start()
			
	elif clientType == "DISPLAY":
		name = RECV(conn)
		if name in clients and not clients[name].displayConn:
			SEND(conn, "ACCEPTED")
			clients[name].displayConn = conn
			print "<" + addr[0] + "> " + name + " DISPLAY connected"
			display = threading.Thread(target=clients[name].DISPLAY)
			display.start()
		else:
			SEND(conn, "FUCK OFF")
			conn.close()
			
	elif clientType == "INPUT":
		name, name1 = RECV(conn).split()
		if name1 in clients[name].activeConnections and name1 not in clients[name].inConns:
			SEND(conn, "ACCEPTED")
			clients[name].inConns[name1] = conn
			print "<" + addr[0] + "> " + name + "-" + name1 + " INPUT connected"
			room = threading.Thread(target=clients[name].ROOM, args=(name1,))
			room.start()
		else:
			SEND(conn, "FUCK OFF")
			conn.close()

	elif clientType == "OUTPUT":
		name, name1 = RECV(conn).split()
		if name1 in clients[name].activeConnections and name1 not in clients[name].outConns:
			SEND(conn, "ACCEPTED")
			clients[name].outConns[name1] = conn
			print "<" + addr[0] + "> " + name + "-" + name1 + " OUTPUT connected"
		else:
			SEND(conn, "FUCK OFF")
			conn.close()


class user:
	def __init__(self, name, conn, addr):
		self.name = name
		self.hubConn = conn
		self.displayConn = None
		self.inConns = {}
		self.outConns = {}
		self.addr = addr
		self.activeConnections = []
		self.pendingInbounds = []
		self.pendingOutbounds = []
		self.running = True
		
	def HUB(self):
		try:
			while True:
				if not self.running:
					try:
						SEND(self.hubConn, "EXIT")
					except:
						pass
					self.hubConn.close()
					return
			
				command = RECV(self.hubConn)
			
				if command.lower() == "help":
					SEND(self.hubConn, "HELP")
					
				elif command.lower() == "log off":
					LOGOFF()
					return
					
				elif command.lower().startswith("connect"):
					if len(command.split()) != 2:
						SEND(self.hubConn, "SHORT")
						continue
					name = command.split()[1]
					if name in clients:
						if name in self.pendingOutbounds:
							SEND(self.hubConn, "CONNECT REPEAT")
						elif name == self.name:
							SEND(self.hubConn, "CONNECT SELF")
						else:
							clients[name].pendingInbounds.append(self.name)
							self.pendingOutbounds.append(name)
							SEND(self.hubConn, "CONNECT SUCCESSFUL")
					else:
						SEND(self.hubConn, "CONNECT UNSUCCESSFUL")
						
				elif command.lower().startswith("accept"):
					if len(command.split()) != 2:
						SEND(self.hubConn, "SHORT")
						continue
					name = command.split()[1]
					if name in self.pendingInbounds:
						self.pendingInbounds.remove(name)
						clients[name].pendingOutbounds.remove(self.name)
						
						SEND(self.hubConn, "ACCEPT SUCCESSFUL")
						SEND(clients[name].hubConn, "ACCEPT SUCCESSFUL")
						time.sleep(0.5)
						SEND(self.hubConn, name)
						SEND(clients[name].hubConn, self.name)
						time.sleep(0.5)
						key = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
						SEND(self.hubConn, key)
						SEND(clients[name].hubConn, key)
						
						self.activeConnections.append(name)
						clients[name].activeConnections.append(self.name)
					else:
						SEND(self.hubConn, "ACCEPT UNSUCCESSFUL")
						
				elif command.lower().startswith("disconnect"):
					if len(command.split()) != 2:
						SEND(self.hubConn, "SHORT")
						continue
					name = command.split()[1]
					if name in self.activeConnections:
						self.DC(name)
						SEND(self.hubConn, "DISCONNECT SUCCESSFUL")
					else:
						SEND(self.hubConn, "DISCONNECT UNSUCCESSFUL")
						
				elif command.lower().startswith("room connect"):
					if len(command.split()) <= 4:
						SEND(self.hubConn, "SHORT")
						continue
					names = command.split()[1:]
					for name in names:
						if name not in clients:
							SEND(self.hubConn, "ROOM CONNECT UNSUCCESSFUL")
							break
						elif name == self.name:
							SEND(self.hubConn, "ROOM CONNECT SELF")
						#elif name in self.pendingOutbounds:
							#SEND(self.hubConn, "CONNECT REPEAT")
					else:
						#clients[name].pendingInbounds.append(self.name)
						#self.pendingOutbounds.append(name)
						SEND(self.hubConn, "ROOM CONNECT SUCCESSFUL")
						
				else:
					SEND(self.hubConn, "INVALID")
		except:
			self.LOGOFF()
			
	def DISPLAY(self):
		try:
			while True:
				if not self.running:
					try:
						SEND(self.displayConn, "EXIT")
					except:
						pass
					self.displayConn.close()
					return
			
				SEND(self.displayConn, str(len(clients)-1))
				for i in clients:
					time.sleep(0.5)
					SEND(self.displayConn, i)
				
				time.sleep(0.5)
				
				SEND(self.displayConn, str(len(self.activeConnections)-1))
				for i in self.activeConnections:
					time.sleep(0.5)
					SEND(self.displayConn, i)
				
				time.sleep(0.5)
				
				SEND(self.displayConn, str(len(self.pendingInbounds)-1))
				for i in self.pendingInbounds:
					time.sleep(0.5)
					SEND(self.displayConn, i)
				
				time.sleep(0.5)
				
				SEND(self.displayConn, str(len(self.pendingOutbounds)-1))
				for i in self.pendingOutbounds:
					time.sleep(0.5)
					SEND(self.displayConn, i)
			
				time.sleep(5)
		except:
			self.LOGOFF()
			
	def ROOM(self, name):
		while name not in self.outConns and self.name not in clients[name].outConns:
			continue
		while True:
			if not self.running:
				try:
					SEND(self.inConns[name], "EXIT")
				except:
					pass
				self.inConns[name].close()
				try:
					SEND(self.outConns[name], "EXIT")
				except:
					pass
				self.outConns[name].close()
				return
		
			try:
				message = RECV(self.inConns[name])
			except:
				self.DC(name)
				return
				
			try:
				SEND(self.outConns[name], message)
			except:
				self.DC(name)
				return
			try:
				SEND(clients[name].outConns[self.name], message)
			except:
				clients[name].DC(self.name)
				return
	
	def DC(self, name):
		if name not in self.activeConnections:
			return
	
		try:
			SEND(self.inConns[name], "EXIT")
			self.inConns[name].close()
		except:
			pass
			
		try:
			SEND(self.outConns[name], "EXIT")
			self.outConns[name].close()
		except:
			pass
		
		try:
			SEND(clients[name].inConns[self.name], "DODGE")
			clients[name].inConns[self.name].close()
		except:
			clients[name].DC(self.name)
		
		try:
			SEND(clients[name].outConns[self.name], "DODGE")
			clients[name].outConns[self.name].close()
		except:
			clients[name].DC(self.name)
		
		del self.inConns[name]
		del self.outConns[name]
		del clients[name].inConns[self.name]
		del clients[name].outConns[self.name]
		self.activeConnections.remove(name)
		clients[name].activeConnections.remove(self.name)
	
	def LOGOFF(self):
		if not self.running:
			return
		self.running = False
		
		try:
			SEND(self.hubConn, "EXIT")
			self.hubConn.close()
		except:
			pass
		
		try:
			SEND(self.displayConn, "EXIT")
			self.displayConn.close()
		except:
			pass
		
		for i in self.inConns:
			try:
				SEND(self.inConns[i], "EXIT")
				self.inConns[i].close()
			except:
				pass
			
		for i in self.outConns:
			try:
				SEND(self.outConns[i], "EXIT")
				self.outConns[i].close()
			except:
				pass
		
		for i in self.activeConnections:
			try:
				SEND(clients[i].inConns[self.name], "DODGE")
			except:
				clients[i].LOGOFF()
				
			try:
				SEND(clients[i].outConns[self.name], "DODGE")
			except:
				clients[i].LOGOFF()
				
			try:
				clients[i].activeConnections.remove(self.name)
			except:
				pass
						
		for i in self.pendingInbounds:
			clients[i].pendingOutbounds.remove(self.name)
			
		for i in self.pendingOutbounds:
			clients[i].pendingInbounds.remove(self.name)
		
		del clients[self.name]
		print "<" + self.addr[0] + "> " + self.name + " logged off"


cipher = AESCipher("")			#####some random string#####
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
IP_address = "0.0.0.0"
Port = 5321
server.bind((IP_address, Port))
server.listen(8)

clients = {}

file = open("names.txt")
names = file.read().splitlines()
file.close()
file = open("passwords.txt")
passwords = file.read().splitlines()
file.close()
file = open("new.txt")
new = file.read().splitlines()
file.close()

os.system("title Server")
		
while True:
	conn, addr = server.accept()
	threading.Thread(target=newConnection, args=(conn, addr)).start()