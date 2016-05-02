# -*- coding: utf-8 -*-
import random
from .fileservice import BackgroundService
from .manager import UploadManager, DownloadManager, UploadServer, PartsChecker
from .handlers import TrackerThread, PeerThread

class Client(object):

	def __init__(self, address, tracker, db):
		self.address = address
		self.port = random.randrange(50000, 65000)
		self.sessionid = None
		self.tracker = tracker
		self.db = db
		self.context = dict()
		self.threads = []
		BackgroundService(self).start()
		UploadManager(self).start()
		DownloadManager(self).start()
		PartsChecker(self).start()
		#self._upman = UploadServer((self.address, self.port), self)
		#self._upman.serve_forever()
		
	def enqueue_download(self, fid):
		self.context["down_queue"].append(fid)

	def login(self):
		thread = TrackerThread(self, "login")
		thread.start()
		thread.join()
		if not self.sessionid:
			print "Exception"
	
	def logout(self):
		thread = TrackerThread(self, "logout")
		thread.start()
		thread.join()
		if self.sessionid:
			print("logout not correct")

	def add(self, **kwargs):
		TrackerThread(self, "add", **kwargs).start()

	def search(self, **kwargs):
		TrackerThread(self, "search", **kwargs).start()
		
	def completeSearch(self, **kwargs):
		TrackerThread(self, "peers", **kwargs).start()
		
	def downloadFile(self, **kwargs):
		PeerThread(self, "download", **kwargs).start()
		

