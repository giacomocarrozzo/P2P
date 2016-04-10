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

## fd00:0000:0000:0000:c864:f17c:bb5e:e4d1 giulio
## fd00:0000:0000:0000:7481:4a85:5d87:9a52 altri
## fd00:0000:0000:0000:22c9:d0ff:fe47:70a3
## fd00:0000:0000:0000:c646:19ff:fe69:b7a5
## fd00:0000:0000:0000:acdf:bd40:555a:59e4
## fd00:0000:0000:0000:9afe:94ff:fe3f:b0f2
## fd00:0000:0000:0000:b89a:58cf:3c32:10a6

## michael fd00:0000:0000:0000:5626:96ff:fedb:a4ad
## marco fd00:0000:0000:0000:e6ce:8fff:fe0a:5e0e
## mahdi fd00:0000:0000:0000:ddb9:fc81:21d4:62c0
## danny fd00:0000:0000:0000:9200:4eff:feb0:0dd4


class Controller(threading.Thread):

	def __init__ (self):
		#super(Controller, self).__init__(**kwargs)
		threading.Thread.__init__(self)

		self.canRun = True
		self.context = dict()
		self.context['peers_index'] = 0
		self.context['file_names'] = list()
		self.context["peers_addr"] = list()
		#self.adapter = la.ListAdapter(data=self.context['file_names'],selection_mode='single',allow_empty_selection=False,cls=lv.ListItemButton)
		#self.peerAdapter = la.ListAdapter(data=self.context['peers_addr'],selection_mode='single',allow_empty_selection=False,cls=lv.ListItemButton)
		##creiamo il database
		self.db = Database(self)

		self.peer = PeerClient(self, '2001:0000:0000:0000:0000:0000:0000:000b')#"fd00:0000:0000:0000:e6ce:8fff:fe0a:5e0e")  
		#self.peer.iamsuper = False
		
		self.receiver = Receiver(self)
		self.background = BackgroundService( self )
		self.cercaVicini = CercaVicini(self)

		#self.adapter.bind(on_selection_change=self.selectedItem)
		#self.fileList.adapter = self.adapter

		#self.peerAdapter.bind(on_selection_change=self.peer.downloadFile)
		#self.peerList.adapter = self.peerAdapter

		self.background.start()
		self.receiver.start()
		self.cercaVicini.start()

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
				print "      1. add near           	 #"
				print "      2. search                #"
				print "      3. download              #"
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
					to_down = raw_input("inserisci dati download: ")
					self.peer.downloadFile(to_down)
				elif choice == "4":
					pass
					#c.logout()
			print "closing app.."
			return
		except KeyboardInterrupt:
			print "closing app.."
			self.stop()
			return

	def stop(self):
		print("chiudo1")
		self.background.stop()
		print("chiudo2")
		self.receiver.stop()
		print("chiudo3")
		self.cercaVicini.stop()
		print("chiudo4")
		self.db.stop()
		print("chiudo5")
		self.canRun = False

	def calcMD5(self, filename):
		m = hashlib.md5()
		readFile = open(str("shared/"+filename) , "r")
		text = readFile.readline()
		while text:
			m.update(text)
			text = readFile.readline()

		digest = m.hexdigest()
		digest = digest[:16]
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
		print "closing app.."


