from Peer.client import PeerClient
from Peer.server import PeerServer
from Services.backgroundService import BackgroundService

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
import os

## fd00:0000:0000:0000:c864:f17c:bb5e:e4d1 giulio
## fd00:0000:0000:0000:7481:4a85:5d87:9a52 altri
## fd00:0000:0000:0000:22c9:d0ff:fe47:70a3
## fd00:0000:0000:0000:c646:19ff:fe69:b7a5
## fd00:0000:0000:0000:acdf:bd40:555a:59e4
## fd00:0000:0000:0000:9afe:94ff:fe3f:b0f2
## fd00:0000:0000:0000:b89a:58cf:3c32:10a6
## fd00:0000:0000:0000:e51b:7f21:0581:d28d
## fd00:0000:0000:0000:7df0:8e22:7cd7:d5b5
## fd00:0000:0000:0000:0000:0000:0000:0010

class Controller(FloatLayout):

	file_source = StringProperty(None)

	def __init__ (self, **kwargs):
		super(Controller, self).__init__(**kwargs)

		self.context = dict()
		self.context['file_names'] = list()
		self.context["peers_addr"] = list()
		self.adapter = la.ListAdapter(data=self.context['file_names'],selection_mode='single',allow_empty_selection=False,cls=lv.ListItemButton)
		self.peerAdapter = la.ListAdapter(data=self.context['peers_addr'],selection_mode='single',allow_empty_selection=False,cls=lv.ListItemButton)

		self.context['my_ip_v4'] = "192.168.43.179";
		self.context['my_ip_v6'] = "fe80:0000:0000:0000:8046:4bbd:91ca:b484";
		self.context['server_ip_v4'] = "192.168.43.100";
		self.context['server_ip_v6'] = "fe80:0000:0000:0000:0a00:27ff:fea0:f155";
		self.context['server_port'] = "3000";

		self.peer = PeerClient()
		self.peer.set(self, self.context['my_ip_v4']+"|"+self.context['my_ip_v6'], self.context['server_ip_v6'],self.context['server_ip_v4'], self.context['server_port'])

		self.peerServer = PeerServer(self)
		self.background = BackgroundService( self )

		self.adapter.bind(on_selection_change=self.selectedItem)
		self.fileList.adapter = self.adapter

		self.peerAdapter.bind(on_selection_change=self.peer.downloadFile)
		self.peerList.adapter = self.peerAdapter

		self.background.start()
		self.peerServer.start()

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
		readFile = open(str(os.path.normcase("shared/"+filename)) , "r")
		text = readFile.readline()
		while text:
			m.update(text)
			text = readFile.readline()

		digest = m.hexdigest()
		digest = digest[:16]
		return digest

	def receivedLogin( self, sessionId ):
		self.context['sessionid'] = sessionId
		self.log(sessionId)

class ControllerApp(App):

	def build(self):
		return Controller()

if __name__ == '__main__':
	ControllerApp().run()
