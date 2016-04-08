import threading
import socket
import string
import random
import sys
import time
import os

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
		while self.canRun:
			try:
				self.app.log("ABOUT TO SEND NEAR")
				print("ABOUT TO SEND NEAR")
				peers = self.app.db.getAllPeers()
				if len(peers) != 0 and len(peers) < 4:
					chars = string.ascii_letters + string.digits
					packetID = "".join(random.choice(chars) for x in range(random.randint(16, 16)))
					for i in range(len(peers)):
						ip , port = peers[i]
						print(peers[i])
						#Random ipv6 ipv4
						if random.randint(0,1)==0:
							print ("ipv4")
							s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
							ip = ip.split("|")[0]
							s.connect((ip, int(port)))
						else:
							print ("ipv6")
							s = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
							ip = ip.split("|")[1]
							s.connect((ip, int(port)))
						#s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
						#s.connect((ip, int(port)))
						self.app.log("sending near to " + str((ip, int(port))))
						print("sending near to " + str((ip, int(port))))
						ttl = "02"
						port_message = ("0" * (5-len(str(self.port)))) + str(self.port)
						message = "NEAR" + packetID + self.address + port_message + ttl
						self.app.log("SENDING " + message)
						print("SENDING " + message)
						s.send(message)
						s.close()
				time.sleep(50)
			except:
				self.numErr += 1
				self.app.log("CERCAVICINI ERRORE", "ERR")
				print(sys.exc_info()[0], "ERR")
				print(sys.exc_info()[1], "ERR")
				print(sys.exc_info()[2], "ERR")
		return
