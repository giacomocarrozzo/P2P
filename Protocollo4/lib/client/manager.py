# -*- coding: utf-8 -*-

import time
import random
import socket
from SocketServer import ThreadingMixIn, TCPServer
from threading import Thread, RLock
from .handlers import PeerThread, Uploader, TrackerThread

lock = RLock()


class UploadServer(ThreadingMixIn, TCPServer):
	daemonize = True
	allow_reuse_address = True
	address_family = socket.AF_INET6
	
	def __init__(self, server_address, client):
		self._client = client
		TCPServer.__init__(self, server_address, Uploader)
		
	#def server_bind(self):
	#	self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, False)
	#	TCPServer.server_bind(self)


class RunnableThread(Thread):
	def __init__(self, client):
		Thread.__init__(self)
		self.isRunnable = True
		self._client = client
		client.threads.append(self)
		
	def stop(self):
		self.isRunnable = False
		
	def run(self):
		while self.isRunnable:
			self.work()
		self._client.threads.remove(self)
		
	def work(self):
		time.sleep(5)

'''
class UploadManager(RunnableThread):
	def __init__(self, client):
		RunnableThread.__init__(self, client)
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def run(self):
		self.s.bind((self._client.address, self._client.port))
		self.s.listen(1)
		RunnableThread.run(self)
		self.s.close()
		
	def stop(self):
		import sys
		sys.exit()
		
	def work(self):
		cs, caddr = self.s.accept()
		msg_type = cs.recv(4)
		if msg_type == "RETP":
			fid = cs.recv(16)
			partn = cs.recv(8)
			thread = PeerThread(self._client, "upload", socket=cs, fid=fid, partn=partn)
			thread.start()
'''
class PartsChecker(RunnableThread):
	def __init__(self, client):
		RunnableThread.__init__(self, client)
	
	def work(self):
		if len(self._client.context['downloading']):
			for i in self._client.context['downloading']:
				fid, fdata = self._client.db.Files.find_by(id=i)[0]
				print "READ FILE ID", i, fdata['id']
				#self._client.completeSearch(choice=fdata['id'], parts=fdata['parts'])
		time.sleep(10)

class UploadManager(RunnableThread):
	def run(self):
		self.server = UploadServer((self._client.address, self._client.port), self._client)
		self.server.serve_forever()
	
	def stop(self):
		self.server.shutdown()
	

class DownloadManager(RunnableThread):
	def __init__(self, client):
		RunnableThread.__init__(self, client)
		self._client.context["down_queue"] = []
		self._client.context["downloading"] = []
		
	@property
	def downloads(self):
		return self._client.context["downloading"]
		
	@property
	def queue(self):
		return self._client.context["down_queue"]
	
	def work(self):
		if len(self.downloads) < 4 and self.queue:
			c = 0
			while self.queue and c < 4:
				d = self.queue.pop(0)
				self._client.context["down_parts_"+d] = []
				self._client.context["down_childs_"+d] = []
				self._client.context["down_queue_"+d] = []
				t = Downloader(self._client, fid=d)
				t.start()
				self.downloads.append(d)
				c += 1
		time.sleep(5)


class Downloader(RunnableThread):
	def __init__(self, client, **kwargs):
		RunnableThread.__init__(self, client)
		self.args = kwargs
		self.LIMIT = 10
	
	@property
	def indown(self):
		return self._client.context["down_parts_"+self.args["fid"]]
	
	@property
	def queue(self):
		return self._client.context["down_queue_"+self.args["fid"]]
	
	@property
	def childs(self):
		return self._client.context["down_childs_"+self.args["fid"]]
	
	def run(self):
		self.fdata = self._client.db.Files.find_by(id=self.args["fid"])[0][1]
		self.enqueue()
		## cycle until all child threads are launched
		RunnableThread.run(self)
		## write file and term
		while True:
			if not self.childs:
				import os
				self._client.context["downloading"].remove(self.args["fid"])
				f = open("temp/"+self.fdata["name"]+".part", "rb")
				fdata = f.read()
				f.close()
				f = open("shared/"+self.fdata["name"], "wb+")
				f.write(fdata)
				f.close()
				os.remove("temp/"+self.fdata["name"]+".part")
				break
			time.sleep(3)
			
	def enqueue(self):
		numparts = self.fdata["parts"]
		for i in range(0, int(numparts)):
			self.queue.append(str(i))
		print self.queue
		pfile = open("temp/"+self.fdata["name"]+".part", "w+")
		lines = "".zfill(int(self.fdata["size"]))
		pfile.write(lines)
		pfile.close()
	
	def work(self):
		if not self.queue:
			print "Finished file"
			self.isRunnable = False
			f_id, f_data = self._client.db.Files.find_by(id=self.args['fid'])[0]
			print "downloaded file, setting status to 1"
			self._client.db.Files[f_id]['status'] = 1
			return
		randomid = self.args["fid"]
		data = self.fdata
		numparts = data["parts"]
		myparts = self._client.db.Parts.find_by(file=randomid)
		todown = self.LIMIT if len(self.queue) >= self.LIMIT else len(self.queue)
		if len(self.indown) < todown:
			mypartsn = [r["n"] for i, r in myparts]
			parts_occ = dict()
			for i in self.queue:
				if i not in mypartsn:
					if i not in self.indown:
						parts_occ[i] = dict(n=0, peers=[])
			peers = self._client.db.Peers.find_by(file=randomid)
			for peerid, peerdata in peers:
				partstr = peerdata["parts"]
				for key in parts_occ.iterkeys():
					if partstr[int(key)] == "1":
						parts_occ[key]["n"] += 1
						parts_occ[key]["peers"].append(peerid)
			sorted_occ = [(k, val) for k, val in parts_occ.items()]
			sorted_occ.sort(key=lambda d: d[1]["n"])
			to_start = sorted_occ[0:todown]
			for p in to_start:
				self.indown.append(p[0])
				peer_choosen = random.choice(p[1]["peers"])
				peer = self._client.db.Peers[peer_choosen]
				pip = peer["ip"]
				pport = peer["port"]
				## lancio il thread
				self.childs.append(PeerThread(self._client, "download", ip=pip, port=pport, fid=randomid, fname=data["name"], part=p[0]))
				self.childs[-1].start()
				#print self.queue
				#print p[0]
				#self.queue.remove(p[0])
		print self.indown
		time.sleep(3)
	
