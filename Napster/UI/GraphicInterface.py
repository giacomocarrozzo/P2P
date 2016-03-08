import threading
import kivy
kivy.require('1.0.5')

from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.adapters import listadapter as la
from kivy.uix import listview as lv

class GraphicInterface(object):

	def __init__ (self,app, peer):

		print("inside ui init")
		##threading.Thread.__init__(self)
		self.app = app
		self.peer = peer

		self.root = Tk()
		self.initializeContent()

	def initializeContent(self):

		print("inside ui initialize")

		##creating layout
		self.frame = Frame(self.root)
		self.frame.pack()

		self.loginButton = Button(self.frame, text="login" , command=self.peer.login)
		##self.loginButton.pack(side=LEFT)
		self.loginButton.grid(row=0, column=0)

		self.logoutButton = Button(self.frame, text="logout", command=self.peer.logout)
		##self.logoutButton.pack(side=LEFT)
		self.logoutButton.grid(row=0, column=1)

		self.exitButton = Button(self.frame, text="exit", command=self.app.stop)
		##self.exitButton.pack(side=LEFT)
		self.exitButton.grid(row=0, column=2)

			

		self.search = Text(self.frame, width=100, height=1, background="yellow")	
		self.search.grid(row=0, column=3, columnspan=15)

		self.searchButton = Button(self.frame, text="search" , command=self.peer.searchFile)
		self.searchButton.grid(row=0, column=19)

		self.fileList = Listbox(self.frame, height=30)
		self.fileList.grid(row=1, column=0, columnspan=3, sticky=N+W+E, padx=10, pady=10)

		
		def onselect(evt):
		    # Note here that Tkinter passes an event object to onselect()
		    w = evt.widget
		    index = int(w.curselection()[0])
		    value = w.get(index)
		    self.log ('You selected item %d: "%s"' % (index, value))

		self.fileList.bind('<<ListboxSelect>>', onselect)


		self.console = Text(self.frame, width=100, height=30)
		##self.console.pack(side=RIGHT)
		self.console.grid(row=1, column=3, columnspan=16)

		self.console.tag_add("LOG", "1.0", "1.4")
		self.console.tag_add("ERR", "1.8", "1.13")
		self.console.tag_add("SUC", "1.0", "1.4")
		self.console.tag_config("LOG", foreground="blue")
		self.console.tag_config("ERR", foreground="RED")
		self.console.tag_config("SUC", foreground="green")


	def start(self):

		print("inside ui start")
		self.root.mainloop()

	def log(self, message , messagetype="LOG"):
		if self.console:			
			self.console.insert(END, "\n"+str(message) , str(messagetype))
