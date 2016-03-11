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


	def set(self, app, ip_p2p, ip_dir="none" , porta_dir="none"):
		print("inside peer set")
		try:
			self.app = app
			self.interface = app

			##we should retrieve our ipv6 address and create a new port
			##self.interface.log([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]])
			##self.ip_p2p = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]][0]
			if ip_p2p == None:

				short_ip = socket.getaddrinfo(socket.gethostname(),None, socket.AF_INET6)[1][4][0]
				short_ip_a = short_ip.split(":")
				last = short_ip_a[-1]
				ip = ""
				for i in short_ip_a:
					if len(i) == 0:
						ip = ip + "0000:0000:0000:"
					else:
						if i == last:
							ip = ip + i
						else:
							ip = ip + i + ":"

				self.ip_p2p = ip

			else:
				self.ip_p2p = ip_p2p

			self.port = str(random.randint(8000,9000))
			##we obtained a new port between 8000 and 9000
			print(self.ip_p2p +":"+self.port)

			if ip_dir == "none" and porta_dir == "none":
				print("non hai inserito l'indirizzo della directory")
			else:
				self.ip_dir = ip_dir
				self.porta_dir = int(porta_dir)
				self.directory = (self.ip_dir , int(self.porta_dir))


			##check if our addresses are in ipv6 format
			if not (self.checkIPV6Format(self.ip_p2p)):
				print("indirizzo non corretto")
				return


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

		self.connection_socket = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
		self.connection_socket.connect(self.directory)
 		##mandiamo il messaggio di login
		message = "LOGI"+str(self.ip_p2p)+"0"+str(self.port)
		self.interface.log(message)
		self.connection_socket.send(message)
		message_type = self.connection_socket.recv(4)
		session_id = self.connection_socket.recv(16)
		self.interface.log("TYPE " + message_type)
		if session_id == “0000000000000000”:
			self.interface.log("Utente già registrato o errore)
		else:
			self.interface.log("SESSION ID "+session_id)
			self.app.receivedLogin( session_id )
			##adding all files
			files = glob.glob(os.path.normcase("shared/*.*")
			for f in files:
				filename = f.split(os.path.normcase("shared/"))[1]
				md5 = str(self.app.calcMD5(filename))
				self.addFile(filename,md5)
		self.connection_socket.close()

	def logout(self):
		if (self.app.context['sessionid']):
			self.connection_socket = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
			self.connection_socket.connect(self.directory)
			##mandiamo messsaggio di logout
			message = "LOGO"+str(self.app.context['sessionid'])
			self.interface.log("SENDING LOGOUT " + message)
			self.connection_socket.send(message)

			message_type = self.connection_socket.recv(4)
			file_deleted = self.connection_socket.recv(3)
			self.interface.log("RECEIVED " + message_type)
			self.interface.log("REMOVED " + file_deleted + " FILES")

			self.connection_socket.close()

	def addFile(self, filename, md5):
		if self.app.context["sessionid"]:
			self.connection_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.connection_socket.connect(self.directory)
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

		if self.app.context["sessionid"]:
			self.connection_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.connection_socket.connect(self.directory)
			##rimozione un file

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
				self.connection_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
				self.connection_socket.connect(self.directory)
				##cerchiamo un file
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
						s = str(nome) + "\t #copie" + str(copie)
						print(str(file_md5) + " - " + str(nome) + " - " + str(copie) )
						self.interface.log(s + " " + str(file_md5))
						self.app.context["peers_addr"].append(s)
						i += 1
						for c in range(copie):
							print("stampiamo i peer")
							ip = self.connection_socket.recv(39)
							port = int(self.connection_socket.recv(5))
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
					self.connection_socket.close()

				else:
					print("sono appena fallito")
					self.interface.peerList.adapter.data = list()
					self.interface.peerList.populate()
					self.connection_socket.close()
					self.interface.log("NON HO TROVATO NESSUN FILE." , "ERR")
			else:
				self.interface.log("non hai ancora un sessionid")
		else:
			print("INSIDE SEARCH errore")

	def downloadFile(self, listadapter, *args):
		try:
			self.interface.log("ABOUT TO DOWNLOAD FROM " + listadapter.selection[0].text)
			s = listadapter.selection[0].text
			i = self.app.context["peers_addr"].index(s)
			print("INSIDE DOWNLOAD ")
			key = str(i)+"_"+str(s)
			if(self.app.context["downloads_available"][str(key)]):
				peer = self.app.context["downloads_available"][str(key)]
				print(peer)
				##possiamo far partire il download del file
				destination = (s , int(peer["porta"]))
				print(destination)
				print(peer["md5"])
				self.connection_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
				self.connection_socket.connect(destination)
				message = "RETR"+str(peer["md5"])
				self.connection_socket.send(message)
				message_type = self.connection_socket.recv(4)
				num_chunks = self.connection_socket.recv(6)
				f = open(os.path.normcase('shared/'+peer["nome"].strip(" ")), "wb")
				if int(num_chunks) > 0 :
					print("num chunks " + str(num_chunks))
					self.interface.progress.max = int(num_chunks)
					for i in range(int(num_chunks)):
						len_chunk = self.connection_socket.recv(5)
						if (int(len_chunk) > 0):
							self.interface.progress.value = self.interface.progress.value + 1
							chunk = self.connection_socket.recv(int(len_chunk))
							#f.write(chunk)
							#print("downloading chunk " + str(len_chunk))
							while len(chunk) < int(len_chunk):
								new_data = self.connection_socket.recv(int(len_chunk)-len(chunk))
								#f.write(new_data)
								chunk = chunk + new_data
							f.write(chunk)
					f.close()

				self.connection_socket.close()
				self.interface.progress.value = 0

				## scriviamo alla directory che abbiamo finito il download
				self.connection_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
				self.connection_socket.connect(self.directory)

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
