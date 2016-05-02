# -*- coding: utf-8 -*-
import threading
import glob
import time
import hashlib
import os

class BackgroundService(threading.Thread):

	def __init__ (self,peer):
		threading.Thread.__init__(self)
		self.peer = peer
		self.canRun = True
		self.setDaemon(True)

	def stop(self):
		self.canRun = False	

	def run(self):
		self.retrieveFiles()
		while self.canRun:
			self.checkFiles()
			time.sleep(30)
		return

	def retrieveFiles(self):
		self.peer.context["files"] = []

	def checkFiles(self):
		#print("checking..")
		temp = glob.glob("shared/*.*")
		#to_remove = list(set(self.peer.context['files']) - set(temp))
		to_add = list(set(temp) - set(self.peer.context['files']))
		#if len(to_remove) > 0 :
		#	for f in to_remove:
		#		filename_rem = f.split("shared/")[1]
		#		md5_rem = self.peer.context["md5_files"][filename_rem]
		#		self.peer.remove(filename_rem,md5_rem)

		if len(to_add) > 0:
			print("FILES ADDED: " + str(to_add))
			for f in to_add:
				filename_add = f.split("shared/")[1]
				md5_add, size_add = self.calcMD5(filename_add)
				print("about to add file with " + filename_add + md5_add + size_add)
				self.peer.add(name=filename_add,id=md5_add,size=size_add)

		self.peer.context["files"] = temp
		self.storeMD5Files()
		#print("stored..")
		#self.printFilesToList()

	def storeMD5Files(self):

		file_list = glob.glob("shared/*.*")
		self.peer.context['md5_files'] = dict()
		self.peer.context['files_md5'] = dict()
		self.peer.context['files_sizes'] = dict()
		for f in file_list:
			filename = f.split("shared/")[1]
			md5, size = self.calcMD5(filename)
			self.peer.context['md5_files'][str(filename)] = md5
			self.peer.context['files_md5'][str(md5)] = filename
			self.peer.context['files_sizes'][str(md5)] = size

	
		
	def calcMD5(self, filename):
		m = hashlib.md5()
		#print os.path.getsize("shared/"+filename)
		readFile = open(str("shared/"+filename) , "r")
		text = readFile.readline()
		while text:
			m.update(text)
			text = readFile.readline()

		digest = m.hexdigest()
		digest = digest[:16]
		#import os, base64
		fsize = str(os.path.getsize(str("shared/"+filename)))

		#return (base64.urlsafe_b64encode(os.urandom(16))[:16], fsize)
		return (digest, fsize)



