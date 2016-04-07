import threading
import socket
import time
import sys
import random
import os
from ipv6utils import *

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
			readFile = open(os.path.normcase(str("shared/"+self.filename)) , "rb")
			##size = os.path.getsize("shared/"+filename)
			index = 0
			data = readFile.read(1024)
			message = "ARET"
			messagetemp = ""
			lunghezze = list()
			bytes = list()
			print("ABOUT TO READ FILE")
			while data:
				lunghezze.append(str(len(data)))
				bytes.append(data)
				print("letti byte " + str(len(data)))
				data = readFile.read(1024)
			## ha terminato di leggere il file
			print("about to send message " + message)
			self.socket.send(message)
			l = len(str(int(len(bytes))))

			l_string = ("0" * (6 - l)) + str(int(len(bytes)))
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
			print("error during upload")
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
		print("MI HANNO CONTATTATO")
		# Ricevuto NEAR: richiesta vicini
		if self.type == "NEAR":
			print()
			self.app.log("NEAR received")
			##abbiamo ricevuto richiesta di vicini
			packetID = self.socket.recv(16)
			ip = self.socket.recv(55)
			port = self.socket.recv(5)
			ttl = self.socket.recv(2)
			res = self.app.db.getPacchetto(packetID)

			# Random IPv4/v6 connection
			if 1:
				print("ipv4")
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				ip_v4 = ip.split("|")[0]
				s.connect((ip_v4, int(port)))
			else:
				print("ipv6")
				s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
				ip_v4 = ip.split("|")[1]
				s.connect((ip_v4, int(port)))
			port_message = ("0" * (5-len(str(self.port)))) + str(self.port)
			message = "ANEA" + packetID + self.address + port_message
			s.send(message)
			s.close()

			# Pacchetto nuovo
			if len(res) == 0:
				self.app.db.insertPacchetto(packetID, ip, port) # lo salvo nel DB
				if int(ttl) > 1: # devo ritrasmetterlo
					peers = self.app.db.getAllPeers()
					if len(peers) != 0:
						for i in range(len(peers)): # rimando la near ai miei vicini
							p_ip , p_port = peers[i]

							# Random IPv4/v6 connection
							if 1:
								print("ipv4")
								s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
								p_ip = p_ip.split("|")[0]
								s.connect((p_ip, int(p_port)))
							else:
								print("ipv6")
								s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
								p_ip = p_ip.split("|")[1]
								s.connect(p_ip, int(p_port))
							ttl = str(int(ttl) - 1)
							ttl = ("0" * (2-len(ttl))) + ttl
							message = "NEAR" + packetID + ip + port + ttl
							print("SENDING " + message)
							self.app.log("SENDING " + message)
							s.send(message)
						s.close()
			self.socket.close()

		# Ricevuto ANEA: trovato un vicino
		if self.type == "ANEA":
			print("ANEA received")
			self.app.log("ANEA received")
			# Recupero i miei vicini e controllo di averne al max tre
			peers = self.app.db.getAllPeers()
			if len(peers) < 4:
				packetID = self.socket.recv(16)
				ip = self.socket.recv(55)
				port = self.socket.recv(5)
				res = self.app.db.getPacchetto(packetID)
				self.app.db.insertPacchetto(packetID, ip, port)
				self.app.db.insertPeer(ip, port)
			self.socket.close()

		# Ricevuto QUER: qualcuno sta cercando qualcosa
		if self.type == "QUER":
			print("QUER received")
			self.app.log("QUER received")

			packetID = self.socket.recv(16)
			ip =  self.socket.recv(55)
			port = self.socket.recv(5)
			ttl = self.socket.recv(2)
			ricerca = self.socket.recv(20)

			res = self.app.db.getPacchetto(packetID)
			if len(res) == 0: # Pacchetto nuovo, devo gestirlo
				print("SEARCHING FOR " + ricerca + " - " + str(len(ricerca)))
				self.app.log("SEARCHING FOR " + ricerca + " - " + str(len(ricerca)))
				self.app.db.insertPacchetto(packetID, ip, port)
				files = self.app.db.searchFile(ricerca.replace(" ", ""))

				if len(files) != 0: # Ho dei files che corrispondono alla ricerca
					
					for i in range(len(files)): # Rispondo al peer interessato con i nomi dei files
						if 1:
							print("ipv4")
							s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
							ip = ip.split("|")[0]
							s.connect((ip, int(port)))
						else:
							print("ipv6")
							s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
							ip = ip.split("|")[1]
							s.connect((ip, int(port)))
						filename, md5 = files[i]
						temp = filename
						print("Passo " + str(i))
						print("File: "+ temp)
						if len(temp) < 100:
							while len(temp) < 100:
								temp = temp + " "
						elif len(temp) > 100:
							temp = temp[0:100]
						port_message = ("0" * (5-len(str(self.port)))) + str(self.port)
						message = "AQUE" + packetID + self.address + port_message + md5 + temp
						print("SENDING " + message)
						self.app.log("SENDING " + message)
						s.send(message)
						s.close()

				# Ripropago la query se il ttl del pacchetto è >1
				if int(ttl) > 1:
					ttl = str(int(ttl) - 1)
					ttl = ("0" * (2-len(ttl))) + ttl
					peers = self.app.db.getAllPeers()

					if len(peers) != 0:
						for i in range(len(peers)):
							p_ip, p_port = peers[i]

							if 1:
								print("ipv4")
								s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
								p_ip = p_ip.split("|")[0]
								s.connect((p_ip, int(p_port)))
							else:
								print("ipv6")
								s = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
								p_ip = p_ip.split("|")[1]
								s.connect((p_ip, int(p_port)))

							port_message = ("0" * (5-len(str(port)))) + str(port)
							message = "QUER" + packetID + ip + port_message + ttl + ricerca
							print("SENDING " + message)
							self.app.log("SENDING " + message)
							s.send(message)
							s.close()
			# Chiudo la socket su cui ho ricevuto il messaggio
			self.socket.close()

		# Ricevuto AQUE: qualcuno ha dei files che corrispondono alla mia ricerca
		if self.type == "AQUE":
			print("AQUE received")
			self.app.log("AQUE received")
			packetID = self.socket.recv(16)
			ip = self.socket.recv(55)
			port = self.socket.recv(5)
			md5 = self.socket.recv(32)
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
		#socket.socket(socket.AF_INET6, socket.SOCK_STREAM).connect((self.address, self.port))
		#self.socket.close()

	def run(self):
		try:
			# Socket creation, binding and listening
			info = socket.getaddrinfo(None, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
			info.sort(key=lambda x: x[0] == socket.AF_INET6, reverse=True)
			for res in info:
				af, socktype, proto, canonname, sa = res
				self.socket = None
				try:
					self.socket = socket.socket(af, socktype, proto)
					self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

					# If supported set IPV6_V6ONLY flag to FALSE
					if af == socket.AF_INET6:
						self.socket.setsockopt(ipproto_ipv6(), ipproto_ipv6only(), False)
						print("Socket is listening. IPv6 and IPv4 BOTH supported")
						print("IP: " + sa[0])
						print("Port: " + str(sa[1]))
					self.socket.bind(sa)
					self.socket.listen(1)
					break
				except socket.error as msg:
						continue
			# Error check
			if self.socket is None:
				print ('Could not open socket')
				sys.exit(2)

			# Service
			while self.canRun:
				try:
					socketclient, address = self.socket.accept()
					msg_type = socketclient.recv(4)

					if msg_type == "RETR": # RETR viene gestito da PeerClient
						print("RETR received")
						self.app.log("RETR received")
						md5 = socketclient.recv(32)
						filename = self.app.context["files_md5"][str(md5)]
						PeerToPeer(filename, socketclient, self.app).start()
					else: # Tutti gli altri messaggi sono gestiti dal PacketHandler
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
