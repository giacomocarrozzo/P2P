import threading
import socket
import time
import sys
##import os

class PeerToPeer(threading.Thread):

	def __init__(self, filename, socket, app):

		threading.Thread.__init__(self)
		self.filename = filename
		self.socket = socket
		self.app = app

	def run(self):
		try:
			##filename = self.app.context["files_md5"][str(self.md5)]
			self.filename = self.filename.strip(" ")
			print("about to open file " + self.filename)
			readFile = open(str("shared/"+self.filename) , "rb")
			##size = os.path.getsize("shared/"+filename)
			index = 0
			data = readFile.read(1024)
			message = "ARET"
			messagetemp = ""
			lunghezze = list()
			bytes = list()
			print("ABOUT TO READ FILE")
			while data:
				##index += 1
				##messagetemp = messagetemp +"0"+str(len(data)) + str(data)
				lunghezze.append(str(len(data)))
				bytes.append(data)
				print("letti byte " + str(len(data)))
				data = readFile.read(1024)
			## ha terminato di leggere il file
			##message = message + str(index) + messagetemp
			##self.socket.send(message)
			print("about to send message " + message)
			self.socket.send(message)
			l = len(str(int(len(bytes))))
			
			l_string = ("0" * (6 - l)) + str(int(len(bytes)))

			##self.socket.send(str(l_string).encode('utf-8'))
			print("about to send message " + str(l_string))
			self.socket.send(str(l_string))

			for i in range(len(bytes)):
				
				l_data = ("0" * (5 - len(str(lunghezze[i]))) + str(lunghezze[i]))
				print("sending data to peer " + str(l_data) + " - " + str(l_data).encode('utf-8'))
				self.socket.send(str(l_data).encode('utf-8'))
				self.socket.sendall(bytes[i])

			self.socket.close()
			return
		except:
			print("SONO ANDATO IN ECCEZZIONE ZIO CAN")
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])
			print(sys.exc_info()[2])
			return

class PacketHandler(threading.Thread):

	def __init__ (self, socket, type, app, address, port):
		threading.Thread.__init__(self)
		self.socket = socket
		self.type = type
		self.app = app
		self.address = address
		self.port = port

	def run(self):
		if self.type == "NEAR":
			print()
			self.app.log("NEAR received")
			##abbiamo ricevuto richiesta di vicini
			packetID = self.socket.recv(16)
			ip = self.socket.recv(39)
			port = self.socket.recv(5)
			ttl = self.socket.recv(2)
			res = self.app.db.getPacchetto(packetID)
			s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			s.connect((ip, int(port)))
			port_message = ("0" * (5-len(str(self.port)))) + str(self.port)
			message = "ANEA" + packetID + self.address + port_message
			s.send(message)
			s.close()
			if len(res) == 0:
				self.app.db.insertPacchetto(packetID, ip, port)
				if int(ttl) > 1:
					peers = self.app.db.getAllPeers()
					if len(peers) != 0:
						for i in range(len(peers)):
							p_ip , p_port = peers[i]
							#port_message = ("0" * (5-len(str(p_port)))) + str(p_port)
							s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
							s.connect((p_ip, int(p_port)))
							ttl = str(int(ttl) - 1)
							ttl = ("0" * (2-len(ttl))) + ttl
							message = "NEAR" + packetID + ip + port + ttl
							print("SENDING " + message)
							self.app.log("SENDING " + message)
							s.send(message)
						s.close()
			self.socket.close()
		if self.type == "ANEA":
			print("ANEA received")
			self.app.log("ANEA received")
			##ci stanno rispondendo con dei vicini
			#recupero i miei vicini e controllo di averne meno di tre
			peers = self.app.db.getAllPeers()
			if len(peers) < 4:
				packetID = self.socket.recv(16)
				ip = self.socket.recv(39)
				port = self.socket.recv(5)
				res = self.app.db.getPacchetto(packetID)
				##if len(res) == 0:
					##non ho mai ricevuto questo pacchetto
				self.app.db.insertPacchetto(packetID, ip, port)
				self.app.db.insertPeer(ip, port)
			self.socket.close()

		if self.type == "QUER":
			print("QUER received")
			self.app.log("QUER received")			
			#abbiamo ricevuto un pacchetto di query
			packetID = self.socket.recv(16)
			ip =  self.socket.recv(39)
			port = self.socket.recv(5)
			ttl = self.socket.recv(2)
			ricerca = self.socket.recv(20)
			#controllo se non ho ricevuto il pacchetto
			res = self.app.db.getPacchetto(packetID)
			if len(res) == 0:
				print("SEARCHING FOR " + ricerca + " - " + str(len(ricerca)))
				self.app.log("SEARCHING FOR " + ricerca + " - " + str(len(ricerca)))
				self.app.db.insertPacchetto(packetID, ip, port)
				files = self.app.db.searchFile(ricerca.replace(" ", ""))
				if len(files) != 0:
					#abbiamo trovato i file
					s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
					s.connect((ip, int(port)))
					for i in range(len(files)):
						filename, md5 = files[i]
						temp = filename
						if len(temp) < 100:
							while len(temp) < 100:
								temp = temp + " "
						elif len(temp) > 100:
							temp = temp[0:100]
						port_message = ("0" * (5-len(str(self.port)))) + str(self.port)
						#"0" + str(self.port)
						message = "AQUE" + packetID + self.address + port_message + md5 + temp
						print("SENDING " + message)
						self.app.log("SENDING " + message)
						s.send(message)
					s.close()
					#non propaghiamo la ricerca
				else:
					if int(ttl) > 1:
						ttl = str(int(ttl) - 1)
						ttl = ("0" * (2-len(ttl))) + ttl
						#propaghiamo la ricerca ai nostri vicini
						peers = self.app.db.getAllPeers()
						if len(peers) != 0:
							for i in range(len(peers)):
								p_ip, p_port = peers[i]
								s = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
								s.connect((p_ip, int(p_port)))
								port_message = ("0" * (5-len(str(port)))) + str(port)
								message = "QUER" + packetID + ip + port_message + ttl + ricerca
								print("SENDING " + message)
								self.app.log("SENDING " + message)
								s.send(message)
								s.close()
			self.socket.close()

			
		if self.type == "AQUE":
			print("AQUE received")
			self.app.log("AQUE received")
			packetID = self.socket.recv(16)
			ip = self.socket.recv(39)
			port = self.socket.recv(5)
			md5 = self.socket.recv(16)
			filename = self.socket.recv(100)
			s = str(filename)
			print(str(md5) + " - " + str(filename))
			print(s + " " + str(md5))
			self.app.log(s + " " + str(md5))
			self.app.context["peers_addr"].append(s)
			self.app.context["peers_index"] += 1
			print("\t" + str(ip) + " " + str(port))
			self.app.log("\t" + str(ip) + " " + str(port))
			self.app.context["peers_addr"].append(str(ip))
			key = str(self.app.context["peers_index"])+"_"+str(ip) 
			self.app.context["downloads_available"][str(key)] = dict()
			self.app.context["downloads_available"][str(key)]["porta"] = port
			self.app.context["downloads_available"][str(key)]["nome"] = filename.replace(" ","")
			self.app.context["downloads_available"][str(key)]["md5"] = md5
			self.app.context["peers_index"] += 1
			self.app.peerList.adapter.data = self.app.context["peers_addr"]
			self.app.peerList.populate()


class Receiver(threading.Thread):

	def __init__ (self, app):

		self.canRun = True
		threading.Thread.__init__(self)
		self.app = app
		self.peer = app.peer 
		self.address = app.peer.ip_p2p
		self.port = int(app.peer.port)

		self.setDaemon(True)
		print("PEER ADDRESS "+ self.address + ":" + str(self.port))
		self.app.log("PEER ADDRESS "+ self.address + ":" + str(self.port), "SUC")

	def startServer ( self ):
		##launching peer server
		pass

	def stop(self):
		##self.interface.log("CLOSING THREAD", "LOG")
		self.canRun = False
		##trying to connect to my own port
		print((self.address, self.port))
		self.app.log((self.address, self.port))
		socket.socket(socket.AF_INET6, socket.SOCK_STREAM).connect((self.address, self.port))
		self.socket.close()
	
	def run(self):
		try:
			self.socket = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
			self.server_address = ( self.address , int(self.port))
			self.socket.bind(self.server_address)
			self.socket.listen(1)
			while self.canRun:
				try:
					socketclient, address = self.socket.accept()
					msg_type = socketclient.recv(4)
					if msg_type == "RETR":
						print("RETR received")
						self.app.log("RETR received")
						md5 = socketclient.recv(16)
						filename = self.app.context["files_md5"][str(md5)]
						PeerToPeer(filename, socketclient, self.app).start()
					else:
						PacketHandler(socketclient, msg_type, self.app, self.address, self.port).start()
					
						
				except:
					print("error in receiver run")
					self.app.log("error in receiver run")
					##self.interface.log("exception inside our server","SUC")
					print(sys.exc_info()[0])
					print(sys.exc_info()[1])
					print(sys.exc_info()[2])
					return
			return
		except:
			print("error in creating socket for receiver")
			self.app.log("error in creating socket for receiver")
			##self.interface.log("something wrong in our peer server. sorry","ERR")
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])
			print(sys.exc_info()[2])
			return