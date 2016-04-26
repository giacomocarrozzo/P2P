from Client.peer import PeerClient

from Server.receiver import Receiver
from Server.cerca import CercaVicini

from Services.backgroundService import BackgroundService
from Services.database import Database

import socket
import random
import threading
import hashlib
import glob
import time
import sys

#marcello 192.168.043.128|fe80:0000:0000:0000:7a31:c1ff:fecd:7dae
#enrico 192.168.043.196|fe80:0000:0000:0000:0226:b6ff:fe78:9cef
#giacomo 192.168.043.179|fe80:0000:0000:0000:0000:8046:4bbd:91ca
#andrea 192.168.043.113|fe80:0000:0000:0000:d253:49ff:fece:9247

class Controller(threading.Thread):

	def __init__ (self):
		threading.Thread.__init__(self)

		self.canRun = True
		self.context = dict()
		self.context['peers_index'] = 0
		self.context['file_names'] = list()
		self.context["peers_addr"] = list()
		self.db = Database(self)

		self.peer = PeerClient(self, '192.168.043.113|fe80:0000:0000:0000:d253:49ff:fece:9247')
		
		self.receiver = Receiver(self)
		self.background = BackgroundService( self )
		self.cercaVicini = CercaVicini(self)

		self.background.start()
		self.receiver.start()
		#self.cercaVicini.start()

	def run(self):
		try:
			while self.canRun:
				print "\n"
				print "################################"
				print "                               #"
				print "      #####  #####  #####      #"
				print "      #   #     ##  #   #      #"
				print "      #####    ##   #####      #"
				print "      #      ##     #          #"
				print "      #     #####   #          #"
				print "                               #"
				print "                               #"
				print "      MENU                     #"
				print "      1. add near           	  #"
				print "      2. search                #"
				print "      3. download              #"
				print "      4. login                 #"
				print "      5. logout                #"
				print "                               #"
				print "                               #"
				print "################################"
				print "\n"
				choice = raw_input("scegli: ")
				if choice == "1":
					ip = raw_input("inserisci indirizzo ip: ")
					port = int(raw_input("inserisci porta: "))
					self.peer.addNear(ip, port)
				elif choice == "2":
					to_search = raw_input("inserisci stringa ricerca: ")
					self.peer.searchFile(to_search)
				elif choice == "3":
					to_down = raw_input("inserisci dati download (IPv4|IPv6_md5_nomeFile): ")
					self.peer.downloadFile(to_down)
				elif choice == "4":
					self.cercaVicini.start()
				elif choice == "5":
					#self.stop()
					self.peer.logout()
			print "closing app.."
			return
		except KeyboardInterrupt:
			print "closing app.."
			self.stop()
			return

	def stop(self):
		print("[LOG] Closing background service...")
		self.background.stop()
		print("[LOG] Closing receiver...")
		self.receiver.stop()
		print("[LOG] Closing supernodes search...")
		self.cercaVicini.stop()
		print("[LOG] Closing DB...")
		self.db.stop()
		print("[LOG] Closing main thread...")
		self.canRun = False

	def calcMD5(self, filename):
		m = hashlib.md5()
		readFile = open(str("shared/"+filename) , "r")
		text = readFile.readline()
		while text:
			m.update(text)
			text = readFile.readline()
		digest = m.hexdigest()
		digest = digest[:32]
		return digest

	def receivedLogin( self, sessionId ):
		self.context['sessionid'] = sessionId
		print "received sessionid", sessionId

if __name__ == '__main__':
	try:
		c = Controller()
		c.start()
	except:
		c.stop()
		print "Closing app..."


