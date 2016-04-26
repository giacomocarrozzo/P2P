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

		while (int(round(time.time())) - now) < 30 and self.canRun: #30
			try:
				peers = self.app.db.getAllPeers()
				if len(peers) != 0:
					chars = string.ascii_letters + string.digits
					packetID = "".join(random.choice(chars) for x in range(random.randint(16, 16)))
					for i in range(len(peers)):
						ip , port = peers[i]
						if random.randint(0,1)==0:
							print("IPV4")
						else:
							print("IPV6")
						if 1:#random.randint(0,1)==0:
							s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
							ip = ip.split("|")[0]
						else:
							s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
							ip = ip.split("|")[1]
						s.connect((ip, int(port)))

						ttl = "04"
						port_message = ("0" * (5-len(str(self.port)))) + str(self.port)
						message = "SUPE" + packetID + self.address + port_message + ttl

						print("[SENDING] [SUPE]: " + message)
						s.send(message)
						s.close()

				time.sleep(20) #20

			except:
				self.numErr += 1
				print("[ERROR] error in near", "ERR")
				print(sys.exc_info()[0], "ERR")
				print(sys.exc_info()[1], "ERR")
				print(sys.exc_info()[2], "ERR")

		if( self.canRun ):
			print("[LOG] Searching finished. About to connect to supernode.")
			self.app.peer.isSearching = False

			# Mi collego
			if not self.app.peer.iamsuper:
				print("[LOG] About to choose a peer")
				l = int(len(self.app.peer.superList))
				print self.app.peer.superList, l
				if l > 0:
					index = random.randint(0, l-1)
					self.app.peer.login(self.app.peer.superList[index])
			else:
				self.app.peer.login( (self.address, int(self.port)) )
		return
