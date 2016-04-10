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

		print("inside peer set")
		try:
			self.app = app
			self.superList = list()
			self.isSearching = True
			self.iamsuper = False
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
			else:
				self.port = str(random.randint(40000, 60000))
			##we obtained a new port between 8000 and 9000
			print(self.ip_p2p +":"+self.port)
			#print("MYADDRESS" + self.ip_p2p +":"+self.port)

			
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

	def login(self, directory):
		try:
			if not self.iamsuper:
				s = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
				self.directory = directory
				s.connect(directory)
				##mandiamo il messaggio di login
				port_message = ("0" * (5 - len(str(self.port)))) + self.port
				message = "LOGI"+str(self.ip_p2p) + port_message
				print("about to send login message " + message)
				print(message)
				s.send(message)
				message_type = s.recv(4)
				session_id = s.recv(16)
				print("TYPE " + message_type)
				print("SESSION ID "+session_id)
				self.app.receivedLogin( session_id )
				s.close()

				##adding all files
				files = glob.glob("shared/*.*")
				for f in files:
					filename = f.split("shared/")[1]
					md5 = str(self.app.calcMD5(filename))
					self.addFile(filename,md5)

				##self.peer_server = PeerServer(self.ip_p2p , self.port , self)
				##self.peer_server.start()

				## initializine background service
				##self.background_service = BackgroundService(self)
				##self.background_service.start()
			else:
				print "I'm super peer, i can't login."
		except Exception as e:
			print("exception in login method")
			traceback.print_exc()

	def addFile(self, filename, md5):
		try:
			if not self.iamsuper:
				if self.app.context["sessionid"]:
					print("about to add a new file " + filename + " - " + md5)
					print("about to add new file " + filename + " - " + md5)
					s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
					s.connect(self.directory)
					##aggiungiamo un file
					temp = filename + (" " *(100 - len(filename)))
					
					message = "ADDF"+self.app.context["sessionid"]+md5+temp
					print("about to send addfile message: " + message)
					print(str(message))
					s.send(message)
	
					message_type = s.recv(4)
					copy_numbers = s.recv(3)
	
					print("received " + message_type + " - num files " + copy_numbers)
					print("RECEIVED " + message_type)
					print("NUMBER OF COPIES: " + copy_numbers)
				else:
					print("non hai ancora un sessionid")
			else:
				print("i'm super, i can't add files.")
		except:
			print("exception in adding new file")
			traceback.print_exc()

	def removeFile(self, filename, md5):
		try:
			if not self.iamsuper:
				if self.app.context["sessionid"]:
					s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
					s.connect(self.directory)
					##aggiungiamo un file
				
					message = "DELF"+self.app.context["sessionid"]+md5
					print("about to send remove file message: "+ message)
					s.send(message)
	
					message_type = s.recv(4)
					copy_numbers = s.recv(3)
					print("RECEIVED message " + message_type + " - numero copie rimosse " + copy_numbers) 
					print("RECEIVED " + message_type)
					print("NUMBER OF COPIES: " + copy_numbers)
			else:
				print("I'm super, i can't remove files")
		except:
			print("exception in removing file")
			traceback.print_exc()


	def searchFile(self, text):
		try:
			if not self.iamsuper:
				searchString = text.zfill(20)[0:20] ##.get("1.0", END)[0:-1]
				print("INSIDE SEARCH " + searchString)
	
				chars = string.ascii_letters + string.digits
				packetID = "".join(random.choice(chars) for x in range(random.randint(16, 16)))
				if not len(searchString) == 0:
					# prima di una nuova ricerca azzero le liste precedenti
					self.app.context["peers_addr"] = list()
					self.app.context["downloads_available"] = dict()
					self.app.context["peers_index"] = 0
					'''
					peers = self.app.db.getAllPeers()
					'''
					print("about to send connection")
	
					temp = searchString
					if len(temp) < 20:
						while len(temp) < 20:
							temp = temp + " "
					elif len(temp) > 20:
						temp = temp[0:20]
					'''
					if len(peers) !=0:
						for i in range(len(peers)):
							ip, port = peers[i]
	
							self.connection_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
							self.connection_socket.connect((ip, int(port)))
	
							ttl = "02"
							port_message = ("0" * (5-len(str(self.port)))) + str(self.port)
							message = "QUER"+packetID+""+self.ip_p2p+""+port_message+""+ttl+""+temp
							print("SENDING " + message)
							self.connection_socket.send(message)
							self.connection_socket.close()
					'''
					#sending query to my directory
					s  = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
					s.connect(self.directory)
					ttl = "02"
					port_message = ("0" * (5-len(str(self.port)))) + str(self.port)
					#message = "FIND"+packetID+""+self.ip_p2p+""+port_message+""+ttl+""+temp
					message = "FIND" + self.app.context['sessionid'] + searchString
					print("sending query message: " + message)
					print("SENDING " + message)
					s.send(message)
					s.close()
			else:
				print("i'm super peer, i can't search files manually")
		except:
			print("EXCEPTION IN SEARCH FILE")
			traceback.print_exc()

	def addNear(self, text, port):
		near_addr = text
		near_port = port
		if near_addr != "" and near_port != "":
			self.app.db.insertPeer(near_addr, near_port)

	def downloadFile(self, text):
		try:
			print("ABOUT TO DOWNLOAD FROM " + text)
			s = text
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
				f = open('shared/'+peer["nome"].strip(" "), "wb")
				if int(num_chunks) > 0 :
					self.app.progress.max = int(num_chunks)
					for i in range(int(num_chunks)):
						len_chunk = self.connection_socket.recv(5)
						if (int(len_chunk) > 0):
							self.app.progress.value = self.app.progress.value + 1
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
				self.app.progress.value = 0

			else:
				print("NOT AVAILABLE")
		except:
			print("exception in download file")
			traceback.print_exc()



	def checkIPV6Format(self, address):
		try:
			socket.inet_pton(socket.AF_INET6, address)
			return True
		except:
			return False
