import threading
import traceback
import socket
import time
import sys
import string
import random
import os
from ipv6utils import *

class PeerToPeer(threading.Thread):

	def __init__(self, filename, socket, app):

		threading.Thread.__init__(self)
		self.filename = filename
		self.socket = socket
		self.app = app
		self.timerFlag = True

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
			print("SONO ANDATO IN ECCEZIONE: inside peer to peer object")
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])
			print(sys.exc_info()[2])
			return

class QueryHandler(threading.Thread):

	def __init__(self, ip, port, dest_ip, dest_port):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.responseList = list()
		self.md5List = list()
		self.nameFiles = list()
		self.dest_ip = dest_ip
		self.dest_port = dest_port

	def saveAque(self, ip, port, md5, filename):
		print("Dentro saveAque")
		port = "0" * (5 - len(str(port))) + str(port)
		print(port)
		self.responseList.append((ip, port, md5, filename))

	def run(self):
		try:
			now = int(round(time.time()))
			while (int(round(time.time())) - now) < 20:
				pass
			#sono passati venti secondi di ricezione dei pacchetti.
			#mando una FIN al destinatario con i risultati della ricerca
			type = "AFIN"
			num = str(len(self.responseList))
			message = type + ""
			for i in range(0, len(self.responseList)):
				ip, port, md5, filename = self.responseList[i]
				if md5 not in self.md5List:
					self.md5List.append(md5)
					self.nameFiles.append(filename)
			str_len_md5 = "0" * (3 - len(str(len(self.md5List)))) + str(len(self.md5List))
			message = message + str_len_md5
			for k in range(0, len(self.md5List)):
				occorrenze = 0
				temp = ""
				message = message + self.md5List[k] + self.nameFiles[k]
				for j in range(0, len(self.responseList)):
					ip, port, md5, filename = self.responseList[j]
					if md5 == self.md5List[k]:
						occorrenze += 1
						temp = str(temp) + str(ip) + str(port)
				str_occ = "0" * (3 - len(str(occorrenze))) + str(occorrenze)
				message = message + str_occ + temp
			if 1:#random.randint(0,1)==0:
				print("[LOG] ipv4")
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.dest_ip = self.dest_ip.split("|")[0]
				s.connect((self.dest_ip, int(self.dest_port)))
			else:
				print("[LOG] ipv6")
				s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
				self.dest_ip = self.dest_ip.split("|")[1]
				s.connect((self.dest_ip, int(self.dest_port)))
			print("about to send afin message")
			s.send(message)
			s.close()
		except:
			print("eccezione in queryhandler run")
			traceback.print_exc()



class PacketHandler(threading.Thread):

	def __init__ (self, socket, type, app, address, port, queryPool):
		threading.Thread.__init__(self)
		self.socket = socket
		self.type = type
		self.app = app
		self.address = address
		self.port = port
		self.peer = self.app.peer
		self.queryPool = queryPool
		#self.queryPool = dict()
		#query pool si tiene in memoria i query handler.

	def run(self):
		if self.type == "SUPE":
			try:
				print("SUPE received")
				##abbiamo ricevuto richiesta di vicini
				packetID = self.socket.recv(16)
				ip = self.socket.recv(55)
				port = self.socket.recv(5)
				ttl = self.socket.recv(2)
				res = self.app.db.getPacchetto(packetID)
				if len(res) == 0:
					self.app.db.insertPacchetto(packetID, ip, port)
					if int(ttl) > 1:
						if not self.peer.iamsuper:
							#non sono un super e devo rispedire il pacchetto
							peers = self.app.db.getAllPeers()
							if len(peers) != 0:
								ttl = str(int(ttl) - 1)
								ttl = ("0" * (2-len(ttl))) + ttl
								for i in range(len(peers)):
									p_ip , p_port = peers[i]

									if 1:#random.randint(0,1)==0:
										print("ipv4")
										s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
										p_ip = p_ip.split("|")[0]
										s.connect((p_ip, int(p_port)))
									else:
										print("ipv6")
										s = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
										p_ip = p_ip.split("|")[1]
										s.connect((p_ip, int(p_port)))

									message = "SUPE" + packetID + ip + str(port) + ttl
									print("SENDING " + message)
									s.send(message)
									s.close()
						else:
							#sono un super peer e posso rispondere
							if 1:#random.randint(0,1)==0:
								print("[LOG] ipv4")
								s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
								ip = ip.split("|")[0]
								s.connect((ip, int(port)))
							else:
								print("[LOG] ipv6")
								s = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
								ip = ip.split("|")[1]
								s.connect((ip, int(port)))
							port_message = ("0" * (5- int(len(str(self.port))))) + str(self.port)
							message = "ASUP" + packetID + self.address + port_message
							s.send(message)
							s.close()
				self.socket.close()
			except:
				print("[ERROR] Error while handling SUPE")
				print(sys.exc_info()[0])
				print(sys.exc_info()[1])
				print(sys.exc_info()[2])

		if self.type == "ASUP":
			print("ASUP received")
			##ci stanno rispondendo i super nodi
			packetID = self.socket.recv(16)
			ip = self.socket.recv(55)
			port = self.socket.recv(5)
			if self.peer.iamsuper:
				res = self.app.db.getPacchetto(packetID)
				if len(res) == 0:
					##non ho mai ricevuto questo pacchetto
					self.app.db.insertPacchetto(packetID, ip, port)
					self.app.db.insertPeer(ip, port)
			else:
				if self.peer.isSearching:
					s = (ip, int(port))
					self.peer.superList.append(s)
			self.socket.close()

		if self.type == "LOGI":
			try:
				#ho ricevuto una richiesta di login
				#dovrei essere un super peer, comunque controllo di esserlo
				print("RECEIVED LOGI")
				if self.peer.iamsuper:
					print("i'm super peer, i can handle this.")
					ip = self.socket.recv(55)
					port = self.socket.recv(5)
					msg = self.app.db.insertClient(ip, port)
					#il db mi restituisce il messaggio di errore per il client se ha cagato fuori
					message = "ALGI" + str(msg)
					self.socket.send(message)
				self.socket.close()
			except:
				print("EXCEPTION IN LOGI")
				print(sys.exc_info()[0])
				print(sys.exc_info()[1])
				print(sys.exc_info()[2])

		# NEW gestione logout
		if self.type == "LOGO":
			try:
				if self.peer.iamsuper:
					sessionID = self.socket.recv(16)
					print("[LOG] Removing all client files")
					n = self.app.db.removeAllClientFiles(sessionID)
					n_delete = "0" * (3 - len(str(n))) + str(n)
					message = "ALGO" + n_delete
					self.socket.send(message)

					self.socket.close()
				else:
					print("[LOG] I'm not a supernode, i cannot handle this")
			except:
				print("[ERROR] Exception in LOGO")
				print(sys.exc_info()[0])
				print(sys.exc_info()[1])
				print(sys.exc_info()[2])

		if self.type == "ALGI":
			try:
				print("received algi")
				if not self.peer.iamsuper:
					#non devo essere super
					#leggo il sessionid
					sessionId = self.socket.recv(16)
					if sessionId == "0000000000000000":
						print("error in my login. check login method, please.")
					else:
						#e' andato tutto bene
						print("correct sessionid, printing.. " + sessionId)
						self.app.context["sessionid"] = sessionId
				else:
					#pacchetto algi ricevuto, lo ignoro
					print("i'm super, ignoring algi packet")
				self.socket.close()
			except:
				print("EXCEPTION in ALGI")
				print(sys.exc_info()[0])
				print(sys.exc_info()[1])
				print(sys.exc_info()[2])

		if self.type == "ADDF":
			try:
				if self.peer.iamsuper:
					print("received addfile")
					print("RECEIVED add file")
					sessionId = self.socket.recv(16)
					md5 = self.socket.recv(32)
					filename = self.socket.recv(100)
					print("SessionID: " + str(sessionId))
					print("MD5: " + str(md5))
					print("Filename: " + str(filename))
					self.app.db.insertDirFile(sessionId, md5, filename)
				else:
					print("ignoring add file")
					print("IM NOT SUPER PEER, IGNORING ADD FILE")
				self.socket.close()
			except:
				print("EXCEPTION receiving addfile")

		if self.type == "DELF":
			try:
				if self.peer.iamsuper:
					print("received remove file")
					print("RECEIVED remove file")
					sessionId = self.socket.recv(16)
					md5 = self.socket.recv(32)
					self.app.db.removeDirFile(sessionId, md5)
				else:
					print("ignoring remove file")
					print("IM NOT SUPER PEER, IGNORING REMOVE FILE")
				self.socket.close()
			except:
				print("EXCEPTION in removing file")
				print(sys.exc_info()[0])
				print(sys.exc_info()[1])
				print(sys.exc_info()[2])

		if self.type == "FIND":
			try:
				if self.peer.iamsuper:
					sessionid = self.socket.recv(16)
					ricerca = self.socket.recv(20)
					print("[RECEIVED] Received FIND, query: " + ricerca)
					ip, port, sessionid = self.app.db.getClient(sessionid)
					print("getClient eseguita")
					#recupero i super peer e mando la query.
					ttl = '02'
					chars = string.ascii_letters + string.digits
					packetID = "".join(random.choice(chars) for x in range(random.randint(16, 16)))
					print("PacketID della find: " + str(packetID))
					self.queryPool[packetID] = QueryHandler(self.address, self.port, ip, port)
					self.queryPool[packetID].start()
					print("QueryPool")
					print(self.queryPool.keys())
					files = self.app.db.searchFile(ricerca.replace(" ", ""))
					print("[LOG] Search finished")
					print(str(len(files)))
					print(files)
					if len(files) != 0:
						#abbiamo trovato i file
						for i in range(len(files)):
							sessionid, md5, filename, checkID = files[i]
							temp = filename
							if len(temp) < 100:
								while len(temp) < 100:
									temp = temp + " "
							elif len(temp) > 100:
								temp = temp[0:100]
							ip, port, sess = self.app.db.getClient(sessionid)
							self.queryPool[packetID].saveAque(ip, port, md5, filename)
							#"0" + str(self.port)
					#devo mandare il pacchetto di query a tutti i miei amici superpeer
					peers = self.app.db.getAllPeers()
					if len(peers) != 0:
						for i in range(len(peers)):
							p_ip , p_port = peers[i]

							if 1:#random.randint(0,1)==0:
								print("ipv4")
								s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
								p_ip = p_ip.split("|")[0]
								s.connect((p_ip, int(p_port)))
							else:
								print("ipv6")
								s = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
								p_ip = p_ip.split("|")[1]
								s.connect((p_ip, int(p_port)))

							port_message = ("0" * (5-len(str(self.port)))) + str(self.port)
							message = "QUER" + packetID + self.address + port_message + ttl + ricerca
							print("SENDING " + message)
							s.send(message)
							s.close()
				else:
					print("i'm not super, i can't receive find packets")
			except:
				print("exception in find method")
				traceback.print_exc()

		if self.type == "QUER":
			try:
				if self.peer.iamsuper:
					print("received query, i'm superpeer")
					print("QUER received")
					#abbiamo ricevuto un pacchetto di query
					packetID = self.socket.recv(16)
					ip =  self.socket.recv(55)
					port = self.socket.recv(5)
					ttl = self.socket.recv(2)
					ricerca = self.socket.recv(20)
					#controllo se non ho ricevuto il pacchetto
					res = self.app.db.getPacchetto(packetID)
					if len(res) == 0:
						print("SEARCHING FOR " + ricerca + " - " + str(len(ricerca)))
						self.app.db.insertPacchetto(packetID, ip, port)
						files = self.app.db.searchFile(ricerca.replace(" ", ""))
						if len(files) != 0:
							#abbiamo trovato i file
							if 1:#random.randint(0,1)==0:
								print("ipv4")
								s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
								ip = ip.split("|")[0]
							else:
								print("ipv6")
								s = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
								ip = ip.split("|")[1]
							s.connect((ip, int(port)))
							for i in range(len(files)):
								session, md5, filename, iduser = files[i]
								ip, porta, iduser = self.app.db.getClient(session)
								temp = filename
								if len(temp) < 100:
									while len(temp) < 100:
										temp = temp + " "
								elif len(temp) > 100:
									temp = temp[0:100]
								port_message = ("0" * (5-len(str(porta)))) + str(porta) # self.port sostituito con porta
								#"0" + str(self.port)
								message = "AQUE" + packetID + ip + port_message + md5 + temp # sostituito self.address con ip
								print("SENDING " + message)
								s.send(message)
							s.close()
						#alla fine propaghiamo la ricerca
						if int(ttl) > 1:
							ttl = str(int(ttl) - 1)
							ttl = ("0" * (2-len(ttl))) + ttl
							#propaghiamo la ricerca ai nostri vicini
							peers = self.app.db.getAllPeers()
							if len(peers) != 0:
								for i in range(len(peers)):
									p_ip , p_port = peers[i]

									if 1:#random.randint(0,1)==0:
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
									s.send(message)
									s.close()
				else:
					print("ignoring query, i'm not super")
				self.socket.close()
			except:
				print("exception in quer received")
				print(sys.exc_info()[0])
				print(sys.exc_info()[1])
				print(sys.exc_info()[2])



		if self.type == "AQUE":
			try:
				if self.app.peer.iamsuper:
					self.timerFlag = False
					print("AQUE received")
					packetID = self.socket.recv(16)
					ip = self.socket.recv(55)
					port = self.socket.recv(5)
					md5 = self.socket.recv(32)
					filename = self.socket.recv(100)
					##devo mandare questa roba al query handler con il packetID
					print("PacketID: " + str(packetID))
					print("ip"+ip+" port"+port+" md5"+md5)
					print(self.queryPool.keys())
					print(self.queryPool[packetID])		
					self.queryPool[packetID].saveAque(ip, port, md5, filename)
				else:
					print("ignoring packet, i'm not super")
			except:
				print("EXCEPTION in AQUE")
				print(sys.exc_info()[0])
				print(sys.exc_info()[1])
				print(sys.exc_info()[2])

		if self.type == "AFIN":
			if 1: #not self.app.peer.iamsuper:
				print("received AFIN")
				num_md5 = self.socket.recv(3)
				print "Numero risultati: ", num_md5
				print("Risultati:")
				if not int(num_md5) == 0:
					for i in range(0, int(num_md5)):
						md5 = self.socket.recv(32)
						filename = self.socket.recv(100)
						s = str(filename).replace(" ","")
						#print(str(md5) + " - " + str(filename))
						#print(s + " " + str(md5))
						self.app.context["peers_addr"].append(s)
						self.app.context["peers_index"] += 1
						num_copy = int(self.socket.recv(3))
						if not num_copy == 0:
							p_ip = self.socket.recv(55)
							p_port = self.socket.recv(5)
							#print("\t" + str(p_ip) + " " + str(p_port))
							self.app.context["peers_addr"].append(str(p_ip))
							key = str(self.app.context["peers_index"])+"_"+str(p_ip)
							self.app.context["downloads_available"][str(key)] = dict()
							self.app.context["downloads_available"][str(key)]["porta"] = p_port
							self.app.context["downloads_available"][str(key)]["nome"] = s
							self.app.context["downloads_available"][str(key)]["md5"] = md5
							self.app.context["peers_index"] += 1
							#print self.app.context['peers_addr']
							print str(p_ip)+"_"+md5+"_"+s
							#self.app.peerList.adapter.data = self.app.context["peers_addr"]
							#self.app.peerList.populate()
			else:
				print("i'm super, ignoring afin")

class Receiver(threading.Thread):

	def __init__ (self, app):

		self.canRun = True
		threading.Thread.__init__(self)
		self.app = app
		self.peer = app.peer
		self.address = app.peer.ip_p2p
		self.port = int(app.peer.port)
		self.queryPool = dict()

		self.setDaemon(True)
		print("PEER ADDRESS "+ self.address + ":" + str(self.port), "SUC")

	def startServer ( self ):
		##launching peer server
		pass

	def stop(self):
		##self.interface.log("CLOSING THREAD", "LOG")
		self.canRun = False
		##trying to connect to my own port
		print((self.address, self.port))
		socket.socket(socket.AF_INET6, socket.SOCK_STREAM).connect((self.address, self.port))
		self.socket.close()

	def run(self):
		try:
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
				except socket.error as msg:
						continue
			# Error check
			if self.socket is None:
				print ('Could not open socket')
				sys.exit(2)

			while self.canRun:
				try:
					socketclient, address = self.socket.accept()
					msg_type = socketclient.recv(4)
					if msg_type == "RETR":
						print("RETR received")
						md5 = socketclient.recv(32)
						filename = self.app.context["files_md5"][str(md5)]
						PeerToPeer(filename, socketclient, self.app).start()
					else:
						PacketHandler(socketclient, msg_type, self.app, self.address, self.port, self.queryPool).start()


				except:
					print("error in receiver run")
					##self.interface.log("exception inside our server","SUC")
					print(sys.exc_info()[0])
					print(sys.exc_info()[1])
					print(sys.exc_info()[2])
					return
			return
		except:
			print("error in creating socket for receiver")
			##self.interface.log("something wrong in our peer server. sorry","ERR")
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])
			print(sys.exc_info()[2])
			return
