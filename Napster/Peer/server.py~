import threading
import socket
##import os

class PeerToPeer(threading.Thread):

	def __init__(self, filename, socket):

		threading.Thread.__init__(self)
		self.filename = filename
		self.socket = socket

	def run(self):
		##filename = self.app.context["files_md5"][str(self.md5)]
		self.filename = self.filename.strip(" ")
		readFile = open(str("shared/"+self.filename) , "rb")
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
		self.address = app.peer.ip_p2p
		self.port = int(app.peer.port)

		self.setDaemon(True)
		print("PEER ADDRESS "+ self.address + ":" + str(self.port), "SUC")

	def startServer ( self ):
		##launching peer server
		pass

	def stop(self):
		##self.interface.log("CLOSING THREAD", "LOG")
		self.canRun = False
		##trying to connect to my own port
		socket.socket(socket.AF_INET6, socket.SOCK_STREAM).connect((self.address, self.port))
		self.socket.close()
	
	def run(self):
		try:
			self.socket = socket.socket(socket.AF_INET6 , socket.SOCK_STREAM)
			self.server_address = ( self.address , int(self.port))
			self.socket.bind(self.server_address)
			self.socket.listen(1)
			while self.canRun:
				print(".")
				try:
					socketclient, address = self.socket.accept()
					msg_type = socketclient.recv(4)
					if msg_type == "RETR":
						md5 = socketclient.recv(16)
						filename = self.app.context["files_md5"][str(md5)]
						PeerToPeer(filename, socketclient).start()
						
				except:
					##self.interface.log("exception inside our server","SUC")
					return
		except:
			##self.interface.log("something wrong in our peer server. sorry","ERR")
			return