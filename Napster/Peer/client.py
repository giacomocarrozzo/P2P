import sys
import socket
import time
import random
import glob
import os

class PeerClient(object):

	## azioni ammesse dal peer
	## login
	## logout
	## storage ( key, value )


	def set(self, app, ip_p2p, ip_dir6="none" ,ip_dir4="none", porta_dir="none"):
		print("inside peer set")
		try:
			self.app = app
			self.interface = app

			##we should retrieve our ipv6 address and create a new port
			##self.interface.log([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]])
			##self.ip_p2p = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]][0]
			self.ip_p2p = ip_p2p

			self.port = str(random.randint(8000,9000))
			##we obtained a new port between 8000 and 9000
			print(self.ip_p2p +":"+self.port)

			if ip_dir6 == "none" and ip_dir4 == "none" and porta_dir == "none" :
				print("non hai inserito l'indirizzo della directory")
			else:
				self.ip_dir6 = ip_dir6
				self.ip_dir4 = ip_dir4
				self.porta_dir = int(porta_dir)
				self.directory6 = (self.ip_dir6 , int(self.porta_dir))
				self.directory4 = (self.ip_dir4 , int(self.porta_dir))

		except:
			print("something wrong, sorry ", "ERR")
			print(sys.exc_info()[0], "ERR")
			print(sys.exc_info()[1], "ERR")
			print(sys.exc_info()[2], "ERR")
			return

	def quit(self):
		##effettuo il logout
		##self.logout()
		##self.peer_server.stopServer()
		##self.background_service.stop();
		##self.interface.log(self.peer_server.isAlive())
		##frame.quit()
		pass

	def login(self):
		if 1:
			self.connection_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
			self.connection_socket.connect(self.directory4)
		else:
			self.connection_socket = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
			self.connection_socket.connect(self.directory6)
 		##mandiamo il messaggio di login
		message = "LOGI"+str(self.ip_p2p)+"0"+str(self.port)
		self.interface.log(message)
		self.connection_socket.send(message)
		message_type = self.connection_socket.recv(4)
		session_id = self.connection_socket.recv(16)
		self.interface.log("TYPE " + message_type)
		if session_id == "0000000000000000":
			self.interface.log("Utente gia' registrato o errore")
		else:
			self.interface.log("SESSION ID "+session_id)
			self.app.receivedLogin( session_id )
			##adding all files
			files = glob.glob(os.path.normcase("shared/*.*"))
			for f in files:
				filename = f.split(os.path.normcase("shared/"))[1]
				md5 = str(self.app.calcMD5(filename))
				self.addFile(filename,md5)

	def logout(self):
			##mandiamo messsaggio di logout
			message = "LOGO"+str(self.app.context['sessionid'])
			self.interface.log("SENDING LOGOUT " + message)
			self.connection_socket.send(message)

			message_type = self.connection_socket.recv(4)
			file_deleted = self.connection_socket.recv(3)
			self.interface.log("RECEIVED " + message_type)
			self.interface.log("REMOVED " + file_deleted + " FILES")


	def addFile(self, filename, md5):
		if self.app.context["sessionid"]:
			##aggiungiamo un file
			temp = filename
			if len(temp) < 100:
				while len(temp) < 100:
					temp = temp + " "
			message = "ADDF"+self.app.context["sessionid"]+md5+temp
			self.interface.log(str(message))
			self.connection_socket.send(message)

			message_type = self.connection_socket.recv(4)
			copy_numbers = self.connection_socket.recv(3)

			self.interface.log("RECEIVED " + message_type)
			self.interface.log("NUMBER OF COPIES: " + copy_numbers)
		else:
			self.interface.log("non hai ancora un sessionid")

	def removeFile(self, filename, md5):
			##rimozione un file
		if self.app.context["sessionid"]:
			message = "DELF"+self.app.context["sessionid"]+md5
			self.connection_socket.send(message)

			message_type = self.connection_socket.recv(4)
			copy_numbers = self.connection_socket.recv(3)
			self.interface.log("RECEIVED " + message_type)
			if copy_numbers == 999:
				self.interface.log("File non trovato")
			else:
				self.interface.log("NUMBER OF COPIES: " + copy_numbers)
		else:
			self.interface.log("non hai ancora un sessionid")

	def searchFile(self):

		searchString = self.interface.searchBox.text ##.get("1.0", END)[0:-1]
		print("INSIDE SEARCH " + searchString)
		if not len(searchString) == 0:

			if self.app.context["sessionid"]:
				print("about to send connection")

				temp = searchString
				if len(temp) < 20:
					while len(temp) < 20:
						temp = temp + " "
				elif len(temp) > 20:
					temp = temp[0:20]

				message = "FIND"+self.app.context["sessionid"]+temp
				self.connection_socket.send(message)
				print("messaggio mandato")
				self.app.context["peers_addr"] = list()
				self.app.context["downloads_available"] = dict()

				message_type = self.connection_socket.recv(4)
				num = int(self.connection_socket.recv(3))

				print("messaggio ricevuto")
				if num != 0:
					print("abbiamo dei file")
					print("NUM " + str(num))
					i = 0
					for f in range(num):
						print("stampiamo file")
						print("INSIDE FOR "+ str(i))
						file_md5 = self.connection_socket.recv(16)
						nome = self.connection_socket.recv(100)
						copie = int(self.connection_socket.recv(3))
						s = str(nome) + "\t #copie:" + str(copie)
						print(s + " md5:" + str(file_md5))
						self.interface.log(s + " " + str(file_md5))
						self.app.context["peers_addr"].append(s)
						i += 1

						for c in range(copie):
							print("stampiamo i peer")
							ip = self.connection_socket.recv(55)
							port = self.connection_socket.recv(5)
							print("peer " + str(ip) + " - " + str(port) )
							self.interface.log("\t" + str(ip) + " " + str(port))
							self.app.context["peers_addr"].append(str(ip))
							key = str(i)+"_"+str(ip)
							self.app.context["downloads_available"][str(key)] = dict()
							self.app.context["downloads_available"][str(key)]["porta"] = port
							self.app.context["downloads_available"][str(key)]["nome"] = nome.strip(" ")
							self.app.context["downloads_available"][str(key)]["md5"] = file_md5
							self.app.context["downloads_available"][str(key)]["numcopie"] = copie
							i += 1

					self.isready = False
					print("ALREADY SET self.isready " + str(self.isready))
					self.interface.peerList.adapter.data = self.app.context["peers_addr"]
					self.interface.peerList.populate()

				else:
					print("sono appena fallito")
					self.interface.peerList.adapter.data = list()
					self.interface.peerList.populate()
					self.interface.log("NON HO TROVATO NESSUN FILE." , "ERR")
			else:
				self.interface.log("non hai ancora un sessionid")
		else:
			print("INSIDE SEARCH errore")

	def downloadFile(self, listadapter, *args):
		try:
			self.interface.log("ABOUT TO DOWNLOAD FROM " + listadapter.selection[0].text)
			s = listadapter.selection[0].text
			s4= s.split("|")[0]
			s6= s.split("|")[1]
			i = self.app.context["peers_addr"].index(s)
			print("INSIDE DOWNLOAD ")
			key = str(i)+"_"+str(s)
			print(key)
			if(self.app.context["downloads_available"][str(key)]):
				peer = self.app.context["downloads_available"][str(key)]
				print(peer)
				##possiamo far partire il download del file

				print(destination)
				print(peer["md5"])


				## scriviamo alla directory che abbiamo finito il download
				if 1:
					self.connection_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
					self.connection_socket.connect(self.directory4)
				else:
					self.connection_socket = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
					self.connection_socket.connect(self.directory6)

				message = "DREG" + self.app.context["sessionid"] + peer["md5"]
				self.connection_socket.send(message)

				ack = self.connection_socket.recv(4)
				n_down = self.connection_socket.recv(5)
				self.interface.log("RECEIVED "+ str(ack))
				self.interface.log("#DOWNLOAD " + str(n_down))
				self.connection_socket.close()
			else:
				print("NOT AVAILABLE")
		except:
			print("exception!!")
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])
			print(sys.exc_info()[2])






	def checkIPV6Format(self, address):
		try:
			socket.inet_pton(socket.AF_INET6, address)
			return True
		except:
			return False
