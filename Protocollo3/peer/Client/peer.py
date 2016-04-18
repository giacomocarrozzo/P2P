import sys
import socket
import time
import random
import glob
import string
import random
import traceback

class PeerClient(object):

	def __init__(self, app , ip_p2p):

		print("[LOG] inside peer set")
		try:
			self.app = app
			self.superList = list()
			self.isSearching = True
			self.iamsuper = False # Se TRUE si comporta come supernodo
			self.directory = None

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
			
			if self.iamsuper:
				self.port = '30000'
				print("[SUPERNODO] " + self.ip_p2p + ":" + self.port)
			else:
				self.port = str(random.randint(40000, 60000))
				print("[NODO] " + self.ip_p2p + ":" + self.port)

			##check if our addresses are in ipv6 format	
			if not (self.checkIPV6Format(self.ip_p2p)):
				print("[ERROR] indirizzo IPv6 non corretto")	
				return	


		except:
			print("[ERROR] error in initializing PeerClient", "ERR")
			print(sys.exc_info()[0], "ERR")
			print(sys.exc_info()[1], "ERR")
			print(sys.exc_info()[2], "ERR")
			return

	def login(self, directory):
		try:
			if not self.iamsuper: # NODO normale, login
				self.directory = directory

				if 1:#random.randint(0,1)==0:
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					directory = ( self.directory[0].split("|")[0], self.directory[1] )
					s.connect(directory)
				else:
					s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
					directory = ( self.directory[0].split("|")[1], self.directory[1] )
					s.connect(directory)

				# Invio il login
				port_message = ("0" * (5 - len(str(self.port)))) + self.port
				message = "LOGI"+str(self.ip_p2p) + port_message
				print("[SENDING] [LOGI]: " + message)

				s.send(message)

				# Ricevo l'ID
				message_type = s.recv(4)
				session_id = s.recv(16)
				print("[RECEIVED] [" + message_type + "] received ID: " + session_id)
				self.app.receivedLogin( session_id )
				s.close()

				# Aggiungo i file
				files = glob.glob("shared/*.*")
				for f in files:
					filename = f.split("shared/")[1]
					md5 = str(self.app.calcMD5(filename))
					self.addFile(filename,md5)

			else: # SUPERNODO, non deve fare login
				print "[LOG] I'm supernode, i can't login."

		except Exception as e:
			print("[ERROR] exception in login")
			traceback.print_exc()

	def addFile(self, filename, md5):
		try:
			if not self.iamsuper: # NODO
				if self.app.context["sessionid"]:
					print("[LOG] about to add a new file " + filename + " - " + md5)
					print("[LOG] about to add new file " + filename + " - " + md5)

					if 1:#random.randint(0,1)==0:
						s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						directory = ( self.directory[0].split("|")[0], self.directory[1] )
						s.connect(directory)
					else:
						s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
						directory = ( self.directory[0].split("|")[1], self.directory[1] )
						s.connect(directory)

					temp = filename + (" " *(100 - len(filename)))				
					message = "ADDF"+self.app.context["sessionid"]+md5+temp
					print("[SENDING] [ADDF]: " + message)
					s.send(message)
	
					message_type = s.recv(4)
					copy_numbers = s.recv(3)

					print("[RECEIVED] [" + message_type + "] number of copies: " + copy_numbers)
					s.close()

				else:
					print("[ERROR]: non hai ancora un sessionid")
			else:
				print("[LOG] I'm supernode, i can't add files.")
		except:
			print("[ERROR]: exception in adding new file")
			traceback.print_exc()

	def removeFile(self, filename, md5):
		try:
			if not self.iamsuper: # NODO
				if self.app.context["sessionid"]:

					if 1:# random.randint(0,1)==0:
						s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						directory = ( self.directory[0].split("|")[0], self.directory[1] )
						s.connect(directory)
					else:
						s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
						directory = ( self.directory[0].split("|")[1], self.directory[1] )
						s.connect(directory)
				
					message = "DELF"+self.app.context["sessionid"]+md5
					print("[SENDING] [DELF]: " + message)
					s.send(message)
	
					message_type = s.recv(4)
					copy_numbers = s.recv(3)

					print("[RECEIVED] [" + message_type + "] number of copies removed: " + copy_numbers)
					s.close()

			else:
				print("[LOG] I'm supernode, i can't remove files")
		except:
			print("[ERROR]: exception in removing file")
			traceback.print_exc()


	def searchFile(self, text):
		try:

			if not self.iamsuper: # NODO
				searchString = text.zfill(20)[0:20]
				print("[LOG] Inside search " + searchString)
	
				chars = string.ascii_letters + string.digits
				packetID = "".join(random.choice(chars) for x in range(random.randint(16, 16)))
				if not len(searchString) == 0:
					# prima di una nuova ricerca azzero le liste precedenti
					self.app.context["peers_addr"] = list()
					self.app.context["downloads_available"] = dict()
					self.app.context["peers_index"] = 0

					print("[LOG] Preparing searchString...")
	
					temp = searchString
					if len(temp) < 20:
						while len(temp) < 20:
							temp = temp + " "
					elif len(temp) > 20:
						temp = temp[0:20]

					# Sending query to my directory
					if 1:#random.randint(0,1)==0:
						s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						directory = ( self.directory[0].split("|")[0], self.directory[1] )
						s.connect(directory)
					else:
						s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
						directory = ( self.directory[0].split("|")[1], self.directory[1] )
						s.connect(directory)

					ttl = "02"
					port_message = ("0" * (5-len(str(self.port)))) + str(self.port)

					message = "FIND" + self.app.context['sessionid'] + searchString

					print("[SENDING] [FIND]: " + message)
					s.send(message)
					s.close()

			else:
				print("[LOG] I'm super peer, i can't search files manually")

		except:
			print("[ERROR]: exception in search file")
			traceback.print_exc()

	def addNear(self, text, port):
		near_addr = text
		near_port = port
		if near_addr != "" and near_port != "":
			self.app.db.insertPeer(near_addr, near_port)

	def downloadFile(self, text):
		try:
			s = text
			i = self.app.context["peers_addr"].index(s)
			print("[LOG] inside DOWNLOAD")
			key = str(i)+"_"+str(s)

			if(self.app.context["downloads_available"][str(key)]):
				peer = self.app.context["downloads_available"][str(key)]

				# Possiamo far partire il download del file
				destination = (s , int(peer["porta"]))
				print("[LOG] About to download file " + text + " with hash " + md5 + " from " + destination)

				# Decido vIP a seconda della lunghezza dell'indirizzo
				if len(s)<20:
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				else:
					s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

				s.connect(destination)
				message = "RETR"+str(peer["md5"])		
				print("[SENDING] [RETR]: " + message)
				self.connection_socket.send(message)

				message_type = self.connection_socket.recv(4)
				num_chunks = self.connection_socket.recv(6)
				print("[RECEIVED] [" + message_type + "] number of chunks: " + num_chunks)

				f = open('shared/'+peer["nome"].strip(" "), "wb")
				if int(num_chunks) > 0 :
					self.app.progress.max = int(num_chunks)
					for i in range(int(num_chunks)):
						len_chunk = self.connection_socket.recv(5)
						print("[RECEIVED] [CHUNK-LENGTH]: " + len_chunk)
						if (int(len_chunk) > 0):
							self.app.progress.value = self.app.progress.value + 1
							chunk = self.connection_socket.recv(int(len_chunk))

							while len(chunk) < int(len_chunk):
								new_data = self.connection_socket.recv(int(len_chunk)-len(chunk))
								chunk = chunk + new_data
							f.write(chunk)
					print("[LOG] status OK, file successfully downloaded")
					f.close()

				self.connection_socket.close()
				self.app.progress.value = 0

			else:
				print("[LOG] File NOT AVAILABLE")
		except:
			print("[ERROR] exception in download file")
			traceback.print_exc()


	def checkIPV6Format(self, address):
		try:
			socket.inet_pton(socket.AF_INET6, address)
			return True
		except:
			return False
