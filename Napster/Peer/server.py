import threading
import socket
import os
import pdb
import contextlib
from ipv6utils import *

class PeerToPeer(threading.Thread):

	def __init__(self, filename, socket):

		threading.Thread.__init__(self)
		self.filename = filename
		self.socket = socket

	def run(self):
		##filename = self.app.context["files_md5"][str(self.md5)]
		self.filename = self.filename.strip(" ")
		print("Dentro run thread")
		readFile = open(os.path.normcase(str("shared/"+self.filename)) , "rb")
		##size = os.path.getsize("shared/"+filename)
		index = 0
		data = readFile.read(1024)
		message = "ARET"
		messagetemp = ""
		lunghezze = list()
		bytes = list()
		while data:
			##index += 1
			##messagetemp = messagetemp +"0"+str(len(data)) + str(data)
			lunghezze.append(str(len(data)))
			bytes.append(data)
			data = readFile.read(1024)
		## ha terminato di leggere il file
		##message = message + str(index) + messagetemp
		##self.socket.send(message)
		self.socket.send(message)
		l = len(str(int(len(bytes))))

		l_string = ("0" * (6 - l)) + str(int(len(bytes)))

		##self.socket.send(str(l_string).encode('utf-8'))
		self.socket.send(str(l_string))

		for i in range(len(bytes)):

			l_data = ("0" * (5 - len(str(lunghezze[i]))) + str(lunghezze[i]))

			self.socket.send(str(l_data).encode('utf-8'))
			self.socket.sendall(bytes[i])

		self.socket.close()
		return



class PeerServer(threading.Thread):

	def __init__ (self, app):

		self.canRun = True
		threading.Thread.__init__(self)
		self.app = app
		self.peer = app.peer
		## Salva gli indirizzi IPv4 e IPv6 separandoli
		self.address4 = app.peer.ip_p2p.split("|")[0]
		self.address6 = app.peer.ip_p2p.split("|")[1]
		self.port = int(app.peer.port)

		print(self.port)

		self.setDaemon(True)
		print("PEER ADDRESS4 "+ self.address4 + ":" + str(self.port), "SUC")
		print("PEER ADDRESS6 "+ self.address6 + ":" + str(self.port), "SUC")

	def startServer ( self ):
		##launching peer server
		pass

	def stop(self):
		##self.interface.log("CLOSING THREAD", "LOG")
		self.canRun = False
		##trying to connect to my own port
		socket.socket(socket.AF_INET6, socket.SOCK_STREAM).connect((self.address, self.port))
		self.socket.close()

	def dual_ipv_support(self):
		# Returns true if kernel allows creating a socket which is able to listen both IPv4 and IPv6 connections
		try:
			if self.sock is not None:
				return not self.sock.getsockopt(ipproto_ipv6(), ipproto_ipv6only())
			else:
				self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
				# Execute block and then close the socket
				with contextlib.closing(self.socket):
					self.sock.setsockopt(ipproto_ipv6(), ipproto_ipv6only(), False)
					return True
		except socket.error:
			return False

	def run(self):

		# Socket creation, binding and listening
		info = socket.getaddrinfo(None, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
		info.sort(key=lambda x: x[0] == socket.AF_INET6, reverse=True)
		for res in info:
			af, socktype, proto, canonname, sa = res
			self.sock = None
			try:

				self.sock = socket.socket(af, socktype, proto)
				self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

				# If supported set IPV6_V6ONLY flag to FALSE
				if af == socket.AF_INET6:
					self.sock.setsockopt(ipproto_ipv6(), ipproto_ipv6only(), False)
					print("Socket is listening. IPv6 and IPv4 BOTH supported")
					print("IP: " + sa[0])
					print("Port: " + str(sa[1]))
				else:
					print("suca")
				self.sock.bind(sa)
				self.sock.listen(1)
				break
			except socket.error as msg:
				continue
		# Error check
		if self.sock is None:
			print ('could not open socket')
			sys.exit(1)

		while self.canRun:
			print(".")
			try:
				socketclient, address = self.sock.accept()
				print("***Request accepted***")
				msg_type = socketclient.recv(4)
				print("Print1")
				if msg_type == "RETR":
					print("inside RETR")
					md5 = socketclient.recv(16)
					print("Ricevuto md5: " + str(md5))
					filename = self.app.context["files_md5"][str(md5)]
					print("Filename: " + str(filename))
					PeerToPeer(filename, socketclient).start()
			except:
				print("Something went WRONG, exception raised")
				#self.interface.log("exception inside our server","SUC")
				return
