import threading
import socket
import string
import random
import sys
import time

class CercaVicini (threading.Thread):

	def __init__(self, app):
		threading.Thread.__init__(self)
		self.app = app
		self.address = self.app.peer.ip_p2p
		self.port = self.app.peer.port
		self.canRun = True
		self.numErr = 0

	def stop(self):
		self.canRun = False

	def run(self):

		now = int(round(time.time()))
		while (int(round(time.time())) - now) < 30:
			try:
				peers = self.app.db.getAllPeers()
				if len(peers) != 0:
					chars = string.ascii_letters + string.digits
					packetID = "".join(random.choice(chars) for x in range(random.randint(16, 16)))
					for i in range(len(peers)):
						ip , port = peers[i]
						s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
						s.connect((ip, int(port)))
						print("sending near to " + str((ip, int(port))))
						ttl = "04"
						port_message = ("0" * (5-len(str(self.port)))) + str(self.port)
						message = "SUPE" + packetID + self.address + port_message + ttl
						print("SENDING " + message)
						s.send(message)
						s.close()
				time.sleep(10)
			except:
				self.numErr += 1
				print("CERCAVICINI ERRORE", "ERR")
				print(sys.exc_info()[0], "ERR")
				print(sys.exc_info()[1], "ERR")
				print(sys.exc_info()[2], "ERR")

		print("PASSATI 10 SECONDI. FINE RICERCA")	
		self.app.peer.isSearching = False
		#mi setto il superPeer a cui sono collegato
		if not self.app.peer.iamsuper:
			print("ABOUT TO CHOOSE SUPER PEER")
			l = int(len(self.app.peer.superList))
			print self.app.peer.superList, l
			if l > 0:
				index = random.randint(0, l-1)
				self.app.peer.login(self.app.peer.superList[index])
		return










