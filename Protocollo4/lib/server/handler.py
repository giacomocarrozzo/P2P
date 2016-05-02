# -*- coding: utf-8 -*-
import traceback

class Handler(object):
	def __init__(self, db):
		self.db = db
		self.methods = dict(
			LOGI=self.login,
			LOGO=self.logout,
			ADDR=self.upload,
			LOOK=self.search,
			FCHU=self.index,
			RPAD=self.downloaded
		)
	
	def handle(self, request):
		self.request = request
		mode = request.recv(4)
		print "Handler::req mode is: "+mode
		method = self.methods.get(mode)
		try:
			return method()
		except Exception as e:
			print str(e)
			return None
		
	def _sessionId(self):
		import os, base64
		return base64.urlsafe_b64encode(os.urandom(16))[:16]
		
	def login(self):
		sid = "0"*16
		try:
			ip, port = self.request.recv(39), self.request.recv(5)
			if not self.db.Sessions.find_by(ip=ip):
				sid = self._sessionId()
				self.db.Sessions.insert(id=sid, ip=ip, port=port)
		except Exception as e:
			print str(e)
		return "ALGI"+sid
	
	def logout(self):
		try:
			sid = self.request.recv(16) #sesionid del logout
			#recupero i file in possesso del sessionid
			print "ABOUT TO LOGOUT ", self.db.Parts.find_by(session=sid)
			userParts = self.db.Parts.find_by(session=sid)
			userfiles = list()
			checkfiles = 0
			numdown = 0
			print "USERPARTS ", userParts
			for k, val in userParts:
				print "USERPARTS VALUES	", val['file'], k
				if (val['file']) not in userfiles:
					#print "val[file] ", val['file']
					#print str(self.db.Files[0])
					#f_data = self.db.Files[int(val['file'])]
					userfiles.append(val['file'])
			'''
			for i in range(0, len(userfiles)):
				f_name, f_id = userfiles[i]
				files_to_check = self.db.Files.find_by(name=f_name)
				if len(files_to_check) > 1:
					numdown += len(self.db.Parts.find_by(file=f_id))
					checkfiles +=1
			if checkfiles == len(userfiles):
				#i file dell'utente sono di dominio pubblico
				rowid = self.db.Sessions.find_by(id=sid)[0][0]
				self.db.Sessions.delete(rowid)
				len_parts = str(len(userParts)).zfill(10)
				return "ALOG"+len_parts
			else:
				ret_num_down = str(numdown).zfill(10)
				return "NLOG"+ret_num_down
			'''
			'''
			for k, val in userfiles:
				if self.db.Sessions.find_by(id=sid):
					sort = dict()
					frid, frdata = self.db.Files.find_by(id=k)[0]
					flen, plen = int(frdata["size"]), int(frdata["psize"])
					fparts = flen/plen + 1 if flen%plen else flen/plen
					prows = self.db.Parts.find_by(file=frid)
					#print prows
					for prow in prows:
						urdata = self.db.Sessions.find_by(id=prow[1]["session"])[0][1]
						if prow[1]["session"] not in sort.iterkeys():
							sort[prow[1]["session"]] = dict(
								ip=urdata["ip"], 
								port=urdata["port"], 
								parts=dict()
							)
						sort[prow[1]["session"]]["parts"][prow[1]["n"]] = 1
					#print sort
					res = []
					for data in sort.itervalues():
						plist = []
						for i in range(0, fparts):
							plist.append(str(data["parts"].get(str(i), 0)))
						blen = fparts/8 + 1 if fparts%8 else fparts/8
						blist = []
						for i in range(0, blen*8, 8):
							cs = "".join(plist[i:i+8])
							blist.append(chr(int(cs.ljust(8, "0"), 2)))
						#res.append(data["ip"]+data["port"]+"".join(blist))
						final_parts = ""
						for j in range(0, len(blist)):
							cell = format(ord(blist[j]), "b")
							#cell = str(bin(int(binascii.hexlify(partslist[j]), 16)))[2:]
							final_parts += cell
						final_parts = final_parts[0:fparts]
						print "BLIST", final_parts
			'''
			tot = 0
			numdown = 0
			for fid in userfiles:
				##vado a recuperare quante parti ci sono in giro per ogni file che ho aggiunto
				##se per ogni file il numero delle parti in giro è uguale ad un multiplo del numero delle parti
				##allora il file è stato già scaricato
				print "MY FILE: " , fid, len(userfiles)
				f_data = self.db.Files[int(fid)]
				ratio = int(f_data['size'])%int(f_data['psize'])
				val = int(self.db.Files[int(fid)]['size'])/int(self.db.Files[int(fid)]['psize'])
				val_sup = val + 1
				my_parts = val if not ratio else val_sup
				file_parts = self.db.Parts.find_by(file=fid)
				if not len(file_parts)%my_parts:
					#vuol dire che abbiamo un multiplo perfetto
					if len(file_parts)/my_parts > 1:
						numdown += len(self.db.Parts.find_by(file=fid))
						tot += 1
						
				if tot == len(userfiles):
					print "tutti i tuoi file sonos stati scaricati, bye!"
					#i file dell'utente sono di dominio pubblico
					rowid = self.db.Sessions.find_by(id=sid)[0][0]
					self.db.Sessions.delete(rowid)
					len_parts = str(len(userParts)).zfill(10)
					return "ALOG"+len_parts
				else:
					ret_num_down = str(numdown).zfill(10)
					return "NLOG"+ret_num_down					
		except:
			print traceback.print_exc()
			print("exception in logout")

		
	def upload(self):
		try:
			sid, fid, flen, plen, fname = \
				self.request.recv(16), self.request.recv(16), \
				self.request.recv(10), self.request.recv(6), self.request.recv(100)
			if self.db.Sessions.find_by(id=sid): 
				if self.db.Files.find_by(id=fid):
					return "AADR"+"0"*8
				fname = fname.lower().replace(" ", "")
				rid = self.db.Files.insert(id=fid, name=fname, size=flen, psize=plen)
				flen = int(flen)
				plen = int(plen)
				if not plen:
					raise Exception
				res = flen/plen + 1 if flen%plen else flen/plen
				print "Parts to store: "+str(res)
				for i in range(0, res):
					self.db.Parts.insert(file=rid, session=sid, n=str(i))
				print self.db.Files._rows
				print self.db.Parts._rows
				return "AADR"+"0"*(8-len(str(res)))+str(res)
		except:
			print traceback.print_exc()
		return None
		
	def search(self):
		try:
			sid, search = self.request.recv(16), self.request.recv(20)
			if self.db.Sessions.find_by(id=sid):
				search = search.lower().replace(" ", "")
				rlist = self.db.Files.find_like("name", search)
				res = []
				for r in rlist:
					fname = r[1]["name"]+" "*(100-len(r[1]["name"]))
					print len(r[1]["id"])
					res.append(r[1]["id"]+fname+r[1]["size"]+r[1]["psize"])
				fnum = "0"*(3-len(str(len(res))))+str(len(res))
				return "ALOO"+fnum+"".join(res)
		except:
			print traceback.print_exc()
		return "ALOO000"
	
	def index(self):
		try:
			sid, fid = self.request.recv(16), self.request.recv(16)
			if self.db.Sessions.find_by(id=sid):
				sort = dict()
				frid, frdata = self.db.Files.find_by(id=fid)[0]
				flen, plen = int(frdata["size"]), int(frdata["psize"])
				fparts = flen/plen + 1 if flen%plen else flen/plen
				prows = self.db.Parts.find_by(file=frid)
				print prows
				for prow in prows:
					urdata = self.db.Sessions.find_by(id=prow[1]["session"])[0][1]
					if prow[1]["session"] not in sort.iterkeys():
						sort[prow[1]["session"]] = dict(
							ip=urdata["ip"], 
							port=urdata["port"], 
							parts=dict()
						)
					sort[prow[1]["session"]]["parts"][prow[1]["n"]] = 1
				print sort
				res = []
				for data in sort.itervalues():
					plist = []
					for i in range(0, fparts):
						plist.append(str(data["parts"].get(str(i), 0)))
					blen = fparts/8 + 1 if fparts%8 else fparts/8
					blist = []
					for i in range(0, blen*8, 8):
						cs = "".join(plist[i:i+8])
						blist.append(chr(int(cs.ljust(8, "0"), 2)))
					res.append(data["ip"]+data["port"]+"".join(blist))
				print res
				unum = "0"*(3-len(str(len(res))))+str(len(res))
				return "AFCH"+unum+"".join(res)
		except:
			print traceback.print_exc()
		return "AFCH000"
	
	def downloaded(self):
		try:
			sid, fid, pnum = self.request.recv(16), self.request.recv(16), self.request.recv(8)
			if self.db.Sessions.find_by(id=sid):
				frid = self.db.Files.find_by(id=fid)[0][0]
				pn = int(pnum)
				## store new part
				self.db.Parts.insert(file=frid, session=sid, n=str(pn))
				## get peer parts
				pparts = self.db.Parts.find_by(file=frid, session=sid)
				ppnum = "0"*(8-len(str(len(pparts))))+str(len(pparts))
				return "APAD"+ppnum
		except:
			print traceback.print_exc()
		return "APAD00000000"

