import sys
import socket
import time
import random
import glob
import string
import random

class PeerClient(object):

	def __init__(self, app , ip_p2p):

		print("inside peer set")
		try:
			self.app = app

			# IP non presente nella chiamata, calcolalo
			if ip_p2p == None or ip_p2p == '':
				print("Calulating IP addresses...")
				short_ip = socket.getaddrinfo(None,None, socket.AF_INET6, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)[1][4][0]
				print("Short_ip: " + short_ip)
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
				ip_v4 = socket.gethostbyname(socket.gethostname())
				self.ip_p2p = ip + "|" + ip_v4
				print("IP: " + self.ip_p2p)
				#self.ip_p2p = ip

			# IP passato nella chiamata
			else:
				self.ip_p2p = ip_p2p
			print("Peer's IP (v4|v6): " + self.ip_p2p)
			self.port = str(random.randint(8000,9000))
			##we obtained a new port between 8000 and 9000
			self.app.log(self.ip_p2p +":"+self.port)
			print(self.ip_p2p +":"+self.port)
			
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

	def searchFile(self):
		try:
			searchString = self.app.searchBox.text
			print("INSIDE SEARCH " + searchString)

			chars = string.ascii_letters + string.digits
			packetID = "".join(random.choice(chars) for x in range(random.randint(16, 16)))
			if not len(searchString) == 0:
				# prima di una nuova ricerca azzero le liste precedenti
				self.app.context["peers_addr"] = list()
				self.app.context["downloads_available"] = dict()
				self.app.context["peers_index"] = 0

				peers = self.app.db.getAllPeers()
				print("about to send connection")

				temp = searchString
				if len(temp) < 20:
					while len(temp) < 20:
						temp = temp + " "
				elif len(temp) > 20:
					temp = temp[0:20]

				if len(peers) !=0:
					for i in range(len(peers)):
						ip, port = peers[i]

						# IPv4/v6 random connection
						if random.randint(0,1)==0:
							print("ipv4")
							self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
							ip = ip.split("|")[0]
							self.connection_socket.connect((ip, int(port)))
						else:
							print("ipv6")
							self.connection_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
							ip = ip.split("|")[1]
							self.connection_socket.connect((ip, int(port)))

						ttl = "02"
						port_message = ("0" * (5-len(str(self.port)))) + str(self.port)
						message = "QUER"+packetID+""+self.ip_p2p+""+port_message+""+ttl+""+temp
						self.app.log("SENDING " + message)
						print("SENDING " + message)
						self.connection_socket.send(message)
						self.connection_socket.close()
		except:
			print("EXCEPTION IN SEARCH FILE")
			print(sys.exc_info()[0], "ERR")
			print(sys.exc_info()[1], "ERR")
			print(sys.exc_info()[2], "ERR")

	def addNear(self):
		near_addr = self.app.nearAddr.text
		near_port = self.app.nearPort.text
		if near_addr != "" and near_port != "":
			self.app.db.insertPeer(near_addr, near_port)

	def downloadFile(self, listadapter, *args):
		try:
			self.app.log("ABOUT TO DOWNLOAD FROM " + listadapter.selection[0].text)
			print("ABOUT TO DOWNLOAD FROM " + listadapter.selection[0].text)
			s = listadapter.selection[0].text
			i = self.app.context["peers_addr"].index(s)
			print("INSIDE DOWNLOAD ")
			key = str(i)+"_"+str(s)
			if(self.app.context["downloads_available"][str(key)]):
				peer = self.app.context["downloads_available"][str(key)]
					
				# IPv4/v6 random connection
				if random.randint(0,1)==0:
					print("ipv4")
					print(peer)
					self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s = s.split("|")[0]
					destination = (s, int(peer["porta"]))
					print(destination)
					print(peer["md5"])
					self.connection_socket.connect(destination)
				else:
					print("ipv6")
					print(peer)
					self.connection_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
					s = s.split("|")[1]
					destination = (s, int(peer["porta"]))
					print(destination)
					print(peer["md5"])
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
							while len(chunk) < int(len_chunk):
								new_data = self.connection_socket.recv(int(len_chunk)-len(chunk))
								chunk = chunk + new_data
							f.write(chunk)
					f.close()

				self.connection_socket.close()
				self.app.progress.value = 0

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
