# -*- coding: utf-8 -*-
import socket
import traceback
import glob
import os
import hashlib
from threading import Thread, RLock
from SocketServer import BaseRequestHandler

KB = 1024
lock = RLock()

class CustomThread(Thread):
	def __init__(self, client, method, **kwargs):
		Thread.__init__(self)
		self._client = client
		self._method = method
		self.args = kwargs
		self.s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		self.s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, False)
		
	def recv(self, lenght):
		return self.s.recv(lenght)
	
	def run(self):
		self.__getattribute__("_"+self._method)()
		try:
			self.s.close()
		except:
			pass

class TrackerThread(CustomThread):
	def __send(self, msg):
		self.s.connect(self._client.tracker)
		print("sending message: " + msg)
		self.s.send(msg)
	
	def _login(self):
		try:
			print("about to send login")
			message = "LOGI" + self._client.address + str(self._client.port)
			self.__send(message)
			msg_type = self.recv(4)
			if msg_type == "ALGI":
				print("ALGI received, reading sessionid")
				sessionid = self.recv(16)
				if sessionid == "0000000000000000":
					print("error in login received 0000000000000000")
				else:
					print("received correct sessionid " + sessionid)
					self._client.sessionid = sessionid
					to_add = glob.glob("shared/*.*")
					for f in to_add:
						filename_add = f.split("shared/")[1]
						md5_add, size_add = self.calcMD5(filename_add)
						print("about to add file with " + filename_add + md5_add + size_add)
						self._addAfterLogin(name=filename_add,id=md5_add,size=size_add)
			else:
				print(msg_type)
				print("bad login")
		except:
			print traceback.format_exc()
			print("EXCEPTION in login")
	
	def _addAfterLogin(self, **kwargs):
		TrackerThread(self._client, "add", **kwargs).start()
		
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
	
	def _logout(self):
		try:
			if self._client.sessionid:
				print("We are logged in, sending logout to tracker.")
				message = "LOGO" + self._client.sessionid
				self.__send(message)
				msg_type = self.recv(4)
				print("reading logout response from server")
				if msg_type == "NLOG":
					#non mi è stato concesso il logout
					partdown = self.recv(10)
					print("Logout not allowed. FILES: " + str(partdown))
				elif msg_type == "ALOG":
					#logout concesso
					partown = self.recv(10)
					self._client.sessionid = None
					print("Logout allowed. See you! FILES: " +str(partown))
			else:
				print("We don't have a sessionid. Do login first.")
		except Exception as e:
			print e.errno, e.strerror, e.value
			print("exception in logout")
			
	def _add(self):
		try:
			print "inside add"
			if self._client.sessionid:
				print("we are logged in, adding files")
				fname = self.args['name'] + " "*(100 - len(self.args['name']))
				fid = self.args['id']
				fsize = "0"*(10 - len(self.args['size'])) + self.args['size']
				plen = 262144
				print("about to send message")
				print("fname" + str(fname) + " .")
				print("fid" + str(fid))
				print("plen" + str(plen))
				print("size" + str(fsize))
				print("sessionid" + self._client.sessionid)
				message = "ADDR" + self._client.sessionid + fid + fsize + str(plen) + fname
				print("sending message " + message + " . " + str(len(message)))
				self.__send(message)
				msg_type = self.recv(4)
				print("reading response from add file to tracker")
				if msg_type == "AADR":
					parts = self.recv(8)
					print("BENE. " + parts)
					#abbiamo correttamente aggiunto il file al tracker, mi salvo il file con status 1
					self._client.db.Files.insert(id=fid, name=self.args["name"], parts=int(parts), status=1)
				else:
					print("qualcosa è andato storto")
			else:
				print "we don't have sessionid, cannot add file"
		except:
			print("exception in add file")
			print traceback.print_exc()
			
	def _search(self):
		try:
			if self._client.sessionid:
				print("we are about to send search message")
				#dovremmo mandare il testo inserito nel campo di ricerca
				to_search = self.args["search"]
				to_search = to_search + " "*(20-len(to_search))
				message = "LOOK" + self._client.sessionid + to_search
				print "about to send message ", message
				self.__send(message)
				msg_type = self.recv(4)
				results = list()
				print("reading response from tracker")
				if msg_type == "ALOO":
					print("received ALOO")
					num = int(self.recv(3))
					if not num == 0: self.results = dict()
					for i in range(0, num):
						randomId = self.recv(16)
						results.append(randomId)
						filename = self.recv(100)
						lenfile = int(self.recv(10))
						lenpart = int(self.recv(6))
						print i, randomId, filename, lenfile, lenpart
						num = lenfile/lenpart + 1 if lenfile%lenpart else lenfile/lenpart
						print num
						fname = filename.replace(" ", "")
						self._client.db.Files.insert(id=randomId, name=fname, parts=num, size=lenfile, status=0)
			else:
				print("you don't have a sessionid, please login first")
		except:
			print("exception in search method")
			print traceback.print_exc()
			
	def _peers(self):
		#import binascii
		try:
			if self._client.sessionid:
				fid = str(self.args["choice"])
				print "FID VALUE: ", fid
				fparts = int(self.args["parts"])
				toread = fparts/8 + 1 if fparts%8 else fparts/8
				print("toread: "+str(toread))
				print("file choosen " + str(fid))
				message = "FCHU" + self._client.sessionid + str(fid)
				print "about to send message ", message
				self.__send(message)
				msg_type = self.recv(4)
				if msg_type == "AFCH":
					print "received AFCH"
					num = int(self.recv(3))
					for i in range(0,num):
						address = self.recv(39)
						port = self.recv(5)
						partslist = self.recv(toread)
						print repr(partslist)
						print type(partslist), str(len(partslist))
						print("partslist "+partslist)
						final_parts = ""
						for j in range(0, toread):
							cell = format(ord(partslist[j]), "b")
							#cell = str(bin(int(binascii.hexlify(partslist[j]), 16)))[2:]
							final_parts += cell
						final_parts = final_parts[0:fparts]
						#print final_parts
						self._client.db.Peers.insert(file=str(fid), ip=address, port=port, parts=final_parts)
						print address, port, final_parts
		except:
			print("exception in _peers method")
			print traceback.print_exc()
			
	def _downloaded(self):
		try:
			if self._client.sessionid:
				fid = self.args["fid"]
				partn = self.args["part"]
				partns = "0"*(8-len(str(partn)))+str(partn)
				message = "RPAD" + self._client.sessionid + fid + partns
				self.__send(message)
				msg_type = self.recv(4)
				if msg_type == "APAD":
					nparts = self.recv(8)
					print "numparts "+nparts
		except:
			print traceback.format_exc()


class PeerThread(CustomThread):
	def __send(self, ip, port, msg):
		self.s.connect((ip, port))
		print("sending message: " + msg)
		self.s.send(msg)
	
	def __chuncks(self, l):
		for i in xrange(0, len(l)):
			yield l[i:i+KB]
	
	def _upload(self):
		try:
			## get file
			rid, rdata = self._client.db.Files.find_by(id=self.args["fid"])[0]
			#controllo lo status. se è 0 vado a leggere dentro tempo
			status = rdata['status']
			if not status:
				f = open("shared/"+rdata["name"], "r")
			else:
				f = open("temp/"+rdata["name"], "r")
			## read part
			f.seek(256*KB*int(self.args["partn"]))
			data = f.read(256*KB)
			f.close()
			## split in chunks
			chunks = self.__chuncks(data)
			## generate response
			res = []
			for chunk in chunks:
				res.append("01024"+chunk)
			cnum = "0"*(6-len(str(len(res))))+str(len(res))
			msg = "AREP"+cnum+"".join(res)
		except:
			print traceback.format_exc()
			msg = "AREP"+"0"*6
		self.args["socket"].send(msg)
	
	def _download(self):
		ip, port = self.args["ip"], self.args["port"]
		randomid, fname, partn = self.args["fid"], self.args["fname"], self.args["part"]
		to_down_temp = "0" * (8 - len(str(partn))) + str(partn)
		try:
			message = "RETP" + randomid + to_down_temp
			self.__send(ip, int(port), message)
			##reading response from peer
			msg_type = self.recv(4)
			fdata = ""
			if msg_type == "AREP":
				numchunk = int(self.recv(6))
				#for i in range(0, numchunk):
				#	len_i = int(self.recv(5))
				#	data = self.recv(len_i)
				#	fdata += data
				#print "received numchunk ", numchunk
				for i in range(numchunk):
					len_chunk = int(self.recv(5))
					#if len_chunk > 0:
					chunk = self.recv(len_chunk)
						#f.write(chunk)
						#print("downloading chunk " + str(len_chunk))
					while len(chunk) < len_chunk:
						new_data = self.recv(len_chunk-len(chunk))
						chunk = chunk + new_data
					fdata += chunk
				lock.acquire()
				if fdata:
					#myparts = self._client.db.Parts.find_by(file=randomid)
					#mypartsn = [r["n"] for i, r in myparts]
					#seek_parts = 0
					#for i in range(0, int(partn)):
					#	if str(i) in mypartsn:
					#		seek_parts += 1
					#try:
					#print "PARTN: "+str(partn)
					pfile = open("temp/"+fname+".part", "r")
					before = pfile.read()
					pfile.close()
					#print "LEN BEFORE: "+str(len(before))
					#print "LEN FDATA: "+str(len(fdata))
					#except:
					#	before = ""
					pfile = open("temp/"+fname+".part", "w")
					try:
						lines = before[0:int(partn)*256*KB]+fdata+before[(int(partn)+1)*256*KB:]
					except:
						lines = before[0:int(partn)*256*KB]+fdata
					#print "LEN LINES: "+str(len(lines))
					pfile.write(lines)
					pfile.close()
					self._client.db.Parts.insert(file=randomid, n=partn)
					tt = TrackerThread(self._client, "downloaded", fid=randomid, part=partn)
					tt.start()
					self._client.context["down_queue_"+randomid].remove(partn)
		except:
			#print traceback.format_exc()
			print "DOWNLOAD HANDLER: error on part "+partn
		finally:
			self._client.context["down_parts_"+randomid].remove(partn)
			try:
				lock.release()
			except:
				pass
			self._client.context["down_childs_"+randomid].remove(self)


class Uploader(BaseRequestHandler):
	def __chuncks(self, l):
		for i in xrange(0, len(l), KB):
			yield l[i:i+KB]
	
	def handle(self):
		try:
			msg_type = self.request.recv(4)
			if msg_type != "RETP":
				raise Exception
			fid = self.request.recv(16)
			partn = self.request.recv(8)
			## get file
			rid, rdata = self.server._client.db.Files.find_by(id=fid)[0]
			status = rdata['status']
			if status:
				f = open("shared/"+rdata["name"], "rb")
			else:
				f = open("temp/"+rdata["name"]+".part", "rb")
			#f = open("shared/"+rdata["name"], "rb")
			## read part
			f.seek(256*KB*int(partn))
			data = f.read(256*KB)
			f.close()
			## split in chunks
			chunks = [c for c in self.__chuncks(data)]
			## generate response
			cnum = "0"*(6-len(str(len(chunks))))+str(len(chunks))
			#print len(cnum)
			#print cnum
			self.request.sendall("AREP"+cnum)
			for chunk in chunks:
				clen = str(len(chunk)).zfill(5)
				#print len(clen)
				#print clen
				self.request.sendall(clen)
				self.request.sendall(chunk)
		except:
			print traceback.format_exc()
		self.request.close()

