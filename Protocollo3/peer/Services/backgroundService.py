import threading
import socket
import glob
import time

class BackgroundService(threading.Thread):

	def __init__ (self,app):
		threading.Thread.__init__(self)
		self.app = app
		self.peer = app.peer
		self.interface = app
		self.canRun = True
		self.setDaemon(True)

	def stop(self):
		self.canRun = False	

	def run(self):
		print(glob.glob("shared/*.*"), "SUC")
		self.retrieveFiles()
		while self.canRun:
			time.sleep(1)
			self.checkFiles()
		return		

	def retrieveFiles(self):

		self.app.context["files"] = glob.glob("shared/*.*")

	def checkFiles(self):

		if self.app.context['files']:
			temp = glob.glob("shared/*.*")
			to_remove = list(set(self.app.context['files']) - set(temp))
			to_add = list(set(temp) - set(self.app.context['files']))
			if len(to_remove) > 0 :
				for f in to_remove:
					filename_rem = f.split("shared/")[1]
					md5_rem = self.app.context["md5_files"][filename_rem]
					print("REMOVED " + filename_rem + " WITH MD5 " + md5_rem, "SUC")
					self.peer.removeFile(filename_rem,md5_rem)
					self.app.db.removeFile(md5_rem)
					self.printFilesToList()



			if len(to_add) > 0  :
				for f in to_add:
					filename_add = f.split("shared/")[1]
					md5_add = self.app.calcMD5(filename_add)
					print("ADDED " + filename_add + " WITH MD5 " + md5_add, "SUC")
					self.peer.addFile(filename_add,md5_add)
					self.app.db.insertFile(filename_add, md5_add)
					self.printFilesToList()


			self.app.context["files"] = temp
			self.storeMD5Files()


			##self.interface.fileList.update_idletasks()


		else:
			self.app.context["files"] = glob.glob("shared/*.*")

	def storeMD5Files(self):

		file_list = glob.glob("shared/*.*")
		self.app.context['md5_files'] = dict()
		self.app.context['files_md5'] = dict()
		for f in file_list:
			filename = f.split("shared/")[1]
			md5 = self.app.calcMD5(filename)
			self.app.context['md5_files'][str(filename)] = md5
			self.app.context['files_md5'][str(md5)] = filename


	def printFilesToList(self):
		file_list = glob.glob("shared/*.*")
		##self.interface.fileList.delete(0, END)
		self.app.context['file_names'] = []
		for f in file_list:
			filename = f.split("shared/")[1]
			##self.interface.fileList.insert(END, filename)
			self.app.context['file_names'].append(filename)
		print self.app.context['file_names']
		##self.interface.fileList.adapter.data = self.app.context['file_names']
		##self.interface.fileList.populate()


