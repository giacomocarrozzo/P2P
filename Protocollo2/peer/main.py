from Client.peer import PeerClient

from Server.receiver import Receiver
from Server.cerca import CercaVicini

from Services.backgroundService import BackgroundService
from Services.database import Database

import kivy
kivy.require('1.0.5')

from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.adapters import listadapter as la
from kivy.uix import listview as lv
from kivy.uix.scatter import Scatter

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

## fd00:0000:0000:0000:1e4b:d6ff:fecd:ba68
## fd00:0000:0000:0000:021a:73ff:fed2:dbf5

## michael fd00:0000:0000:0000:5626:96ff:fedb:a4ad
## marco fd00:0000:0000:0000:e6ce:8fff:fe0a:5e0e
## mahdi fd00:0000:0000:0000:ddb9:fc81:21d4:62c0


class Controller(FloatLayout):

	file_source = StringProperty(None)

	def __init__ (self, **kwargs):
		super(Controller, self).__init__(**kwargs)

		self.context = dict()
		self.context['peers_index'] = 0
		self.context['file_names'] = list()
		self.context["peers_addr"] = list()
		self.adapter = la.ListAdapter(data=self.context['file_names'],selection_mode='single',allow_empty_selection=False,cls=lv.ListItemButton)
		self.peerAdapter = la.ListAdapter(data=self.context['peers_addr'],selection_mode='single',allow_empty_selection=False,cls=lv.ListItemButton)
		##creiamo il database
		self.db = Database(self)

		self.peer = PeerClient(self, 'fd00:0000:0000:0000:e6ce:8fff:fe0a:5e0e')#"fd00:0000:0000:0000:e6ce:8fff:fe0a:5e0e")  
		self.peer.iamsuper = False

		self.receiver = Receiver(self)
		self.background = BackgroundService( self )
		self.cercaVicini = CercaVicini(self)

		self.adapter.bind(on_selection_change=self.selectedItem)
		self.fileList.adapter = self.adapter

		self.peerAdapter.bind(on_selection_change=self.peer.downloadFile)
		self.peerList.adapter = self.peerAdapter

		self.background.start()
		self.receiver.start()
		self.cercaVicini.start()

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

	def log(self, message, messagetype="LOG"):

		self.console.text = self.console.text + "\n" + str(message)

	def selectedItem(self, listadapter, *args):
		if (len(self.adapter.selection) > 0):
			##print(listadapter)
			##print(args)
			print(self.adapter.selection[0].text)
			##self.fileImage = Scatter(source='shared/'+self.adapter.selection[0].text)
			##self.add_widget(self.fileImage)
			##print(str(self.file_source))

	def calcMD5(self, filename):
		m = hashlib.md5()
		readFile = open(str("shared/"+filename) , "r")
		text = readFile.readline()
		while text:
			m.update(text)
			text = readFile.readline()

		digest = m.hexdigest()
		#digest = digest[:16]
		return digest

	def receivedLogin( self, sessionId ):
		self.context['sessionid'] = sessionId
		self.log(sessionId)

class ControllerApp(App):

	def on_start(self):
		print("sono partito")

	def on_stop(self):
		print("mi sono chiuso")
		self.controller.stop()

	def build(self):
		self.controller = Controller()
		return self.controller

if __name__ == '__main__':
	ControllerApp().run()