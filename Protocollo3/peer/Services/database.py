import sqlite3
import time
import os.path
import threading
import sys
import string
import traceback
import random
from string import *

class DBControl(threading.Thread):

	def __init__ (self):
		threading.Thread.__init__(self)
		self.canRun = True

	def stop(self):
		self.canRun = False

	def run(self):
		while self.canRun:
			if (os.path.isfile('database')):
				try:
					conn = sqlite3.connect("database")
					cursor = conn.cursor()

					select = "SELECT * FROM pacchetti"
					cursor.execute(select)
					results = cursor.fetchall()
					conn.commit()
					cursor.close()
					if len(results) != 0:
						conn = sqlite3.connect("database")
						cursor = conn.cursor()
						for  i in range(len(results)):
							p_id, t , ip , port = results[i]
							if (time.time() - t) > 300:
								
								remove = "DELETE FROM pacchetti WHERE packetID='"+p_id+"'"
								cursor.execute(remove)

						conn.commit()
						cursor.close()

					time.sleep(30)
				except:
					print("something wrong, sorry ", "ERR")
					print(sys.exc_info()[0], "ERR")
					print(sys.exc_info()[1], "ERR")
					print(sys.exc_info()[2], "ERR")
		return

class Database(object):

	def initializeDatabase(self):
		try:
			print("about to initialize db")
			conn = sqlite3.connect('database')
			cursor = conn.cursor()

			c_str = '''CREATE TABLE vicini (ip TEXT, port INT)'''
			cursor.execute(c_str)
			c_str = '''CREATE TABLE pacchetti (packetID TEXT NOT NULL, time INT NOT NULL, peer_ip TEXT , peer_port INT)'''
			cursor.execute(c_str)
			c_str = '''CREATE TABLE files (filename TEXT NOT NULL, md5 TEXT NOT NULL)'''
			cursor.execute(c_str)
			c_str = '''CREATE TABLE dir_files (sessionId TEXT NOT NULL, md5 TEXT NOT NULL, filename TEXT, id  TEXT PRIMARY KEY NOT NULL)'''
			##ID DEL FILE COMPOSTO DA SESSIONID:MD5
			cursor.execute(c_str)
			c_str = '''CREATE TABLE client (ip TEXT, port INT, sessionId TEXT PRIMARY KEY NOT NULL)'''
			cursor.execute(c_str)	
			c_str = '''CREATE TABLE download (md5 TEXT NOT NULL, count INTEGER,PRIMARY KEY (md5) )'''
			cursor.execute(c_str)

			conn.commit()
			cursor.close()
		except:
			print("error in initialize db ", "ERR")
			print(sys.exc_info()[0], "ERR")
			print(sys.exc_info()[1], "ERR")
			print(sys.exc_info()[2], "ERR")
			return

	def __init__(self, app):

		self.app = app
		self.dbControl = DBControl()
		self.dbControl.start()
		if not os.path.isfile('database'):
			self.initializeDatabase()
    	
	def stop(self):
		self.dbControl.stop()

	def random_sessionID(self):
		chars = string.ascii_letters + string.digits
		return "".join(random.choice(chars) for x in range(random.randint(16, 16)))

	def insertClient(self, ip, port):
		try:
			print "about to insert new client", ip, str(port)
			conn = sqlite3.connect("database")
			cursor = conn.cursor()
			select = "SELECT * FROM client WHERE ip='"+ip+"' AND port='"+str(port)+"'"
			cursor.execute(select)
			results = cursor.fetchall()
			if len(results) > 0:
				#abbiamo gia inserito questo client, ritorno il codice di errore
				conn.commit()
				cursor.close()
				return "0000000000000000"
			else:
				#utente mai inserito, creiamo un nuovo sessionid, e inseriamo nel db
				sessionid = self.random_sessionID()
				insert = "INSERT INTO client VALUES(?, ?, ?)"
				values = (ip, int(port), sessionid)
				cursor.execute(insert,values)
				conn.commit()
				cursor.close()
				return sessionid
		except:
			print("EXCEPTION inserting new client, returning error code")
			traceback.print_exc()
			return "0000000000000000"

	def removeClient(self, sessionId):
		try:
			print("trying to remove client with sessionId " + sessionId)
			#prima controllo di averlo nel database
			conn = sqlite3.connect('database')
			cursor = conn.cursor()
			select = "SELECT * FROM client WHERE sessionId='"+str(sessionId)+"'"
			cursor.execute(select)
			results = cursor.fetchall()
			if not len(results) == 0:
				select = "DELETE FROM client WHERE sessionId='"+str(sessionId)+"'"
				cursor.execute(select)
			else:
				print("client not in db, impossible to remove")
			conn.commit()
			cursor.close()
		except:
			print("EXCEPTION trying to remove client with sessionid " + sessionId)
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])
			print(sys.exc_info()[2])	

	def getClient(self, sessionId):
		try:
			print("about to retrieve client with sessionid " + sessionId)
			print "client select all results ", self.getAllClients()
			conn = sqlite3.connect("database")
			cursor = conn.cursor()
			select = "SELECT * FROM client WHERE sessionId='"+str(sessionId)+"'"
			cursor.execute(select)
			results = cursor.fetchall()
			ip, port, id = results[0]
			conn.commit()
			cursor.close()
			return (ip, int(port), id)
		except:
			print("EXCEPTION trying to retrieve client with sessionid " + sessionId)
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])
			print(sys.exc_info()[2])
			return (None, None, None)

	def getAllClients(self):
		try:
			print "about to retrieve all clients"
			conn = sqlite3.connect("database")
			cursor = conn.cursor()
			select = "SELECT * FROM client"
			cursor.execute(select)
			results = cursor.fetchall()
			conn.commit()
			cursor.close()
			print "inside get all clients, about to return all clients"
			return results
		except:
			print("EXCEPTION trying to retrieve all clients")
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])
			print(sys.exc_info()[2])
			return []


	def insertDirFile(self, sessionId, md5, file):
		try:
			print("about to add new file")
			#controllo che lo stesso file non sia gia stato inserito
			id  = str(sessionId) + ":" + str(md5)
			conn = sqlite3.connect("database")
			cursor = conn.cursor()
			select = "SELECT * FROM dir_files WHERE id='"+str(id)+"'"
			cursor.execute(select)
			results = cursor.fetchall()
			if len(results) == 0:
				#nonabbiamo mai inserito questo file, possiamo inserirlo
				insert = "INSERT INTO dir_files VALUES(?, ?, ?, ?)"
				values = (str(sessionId), str(md5), str(file), str(id))
				cursor.execute(insert, values)
				conn.commit()
				cursor.close()
				print("add new file completed successfully")
			else:
				conn.commit()
				cursor.close()

		except:
			print("EXCEPTION in add new file")
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])
			print(sys.exc_info()[2])

	def removeDirFile(self, sessionId, md5):
		try:
			print("about to remove file")
			#controllo che il file sia presente nel db
			id  = str(sessionId) + ":" + str(md5)
			conn = sqlite3.connect("database")
			cursor = conn.cursor()
			select = "SELECT * FROM dir_files WHERE id='"+str(id)+"'"
			cursor.execute(select)
			results = cursor.fetchall()
			if not len(results) == 0:
				#il file e' presente e lo posso cancellare
				delete = "DELETE FROM dir_files WHERE id='"+str(id)+"'"
				cursor.execute(delete)
				conn.commit()
				cursor.close()
				print("remove file completed successfully")
			else:
				conn.commit()
				cursor.close()

		except:
			print("EXCEPTION in remove file")
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])
			print(sys.exc_info()[2])

	def removeAllClientFiles(self, sessionId):
		try:
			print("about to remove all client files")
			#rimuovo il client dal db, e rimuovo tutti i suoi file
			removeClient(sessionId)
			conn = sqlite3.connect("database")
			cursor = conn.cursor()
			select = "SELECT * FROM dir_files WHERE sessionId='"+sessionId+"'"
			cursor.execute(select)
			results = cursor.fetchall()
			if not len(results) == 0:
				# il nostro utente ha inserito qualcosa
				print("deleting user files..")
				deleted = len(results)
				delete = "DELETE FROM dir_files WHERE sessionId='"+sessionId+"'"
				cursor.execute(delete)
				print("returning number of removed files")
				conn.commit()
				cursor.close()
				return len(results)
			else:
				conn.commit()
				cursor.close()
				return 0
		except:
			print("EXCEPTION in remove all client files")
			print(sys.exc_info()[0])
			print(sys.exc_info()[1])
			print(sys.exc_info()[2])
			return 0

	def insertPeer(self, ip, port):
		conn = sqlite3.connect('database')
		cursor = conn.cursor()

		select = "SELECT * FROM vicini WHERE ip='"+ip+"'"
		cursor.execute(select)
		results =  cursor.fetchall()
		if len(results) == 0:
			#non abbiamo mai inserito questo peer
			peer = (ip, int(port))
			query = "INSERT INTO vicini VALUES(?, ?)"
			cursor.execute(query, peer)
		conn.commit()
		cursor.close()

	def insertPacchetto(self, packetID, peer_ip, peer_port):
		conn = sqlite3.connect('database')
		cursor = conn.cursor()

		select = "SELECT * FROM pacchetti WHERE packetID='"+packetID+"'"
		cursor.execute(select)
		results =  cursor.fetchall()
		if len(results) == 0:
			#non abbiamo mai inserito questo pacchetto
			t = time.time()
			pacchetto = (packetID , int(t) , peer_ip , int(peer_port))
			query = "INSERT INTO pacchetti VALUES(?, ?, ?, ?)"
			cursor.execute(query,pacchetto)
		conn.commit()
		cursor.close()

	def insertFile(self, filename, md5):
		conn = sqlite3.connect('database')
		cursor = conn.cursor()

		select = "SELECT * FROM files WHERE md5='"+md5+"'"
		cursor.execute(select)
		results =  cursor.fetchall()
		if len(results) == 0:
			#non abbiamo mai inserito questo pacchetto
			f = (filename, md5)
			query = "INSERT INTO files VALUES(?, ?)"
			cursor.execute(query, f)
		conn.commit()
		cursor.close()

	def searchFile(self, filename):
		conn = sqlite3.connect('database')
		cursor = conn.cursor()

		select = "SELECT * FROM dir_files WHERE UPPER(filename) LIKE UPPER('%"+filename+"%')"
		cursor.execute(select)
		results =  cursor.fetchall()
		conn.commit()
		cursor.close()
		return results

	def getFile(self, md5):
		conn = sqlite3.connect('database')
		cursor = conn.cursor()

		select = "SELECT * FROM files WHERE md5='"+md5+"'"
		cursor.execute(select)
		result =  cursor.fetchall()
		conn.commit()
		cursor.close()
		return result

	def getFileName(self, md5):
		conn = sqlite3.connect('database')
		cursor = conn.cursor()

		select = "SELECT * FROM files WHERE md5='"+md5+"'"
		cursor.execute(select)
		result =  cursor.fetchall()
		if len(result) != 0:
			filename, md5 = result[0]
			conn.commit()
			cursor.close()
			return filename
		else:
			conn.commit()
			cursor.close()
			return None
			

	def getFileMd5(self, filename):
		conn = sqlite3.connect('database')
		cursor = conn.cursor()

		select = "SELECT * FROM files WHERE filename='"+filename+"'"
		cursor.execute(select)
		result =  cursor.fetchall()
		if len(result) != 0:
			filename, md5 = result[0]
			conn.commit()
			cursor.close()
			return md5
		else:
			conn.commit()
			cursor.close()
			return None

	def removeFile(self, md5):
		conn = sqlite3.connect('database')
		cursor = conn.cursor()
		select = "DELETE FROM files WHERE md5='"+md5+"'"
		cursor.execute(select)
		conn.commit()
		cursor.close()


	def removePacchetto(self, packetID):
		conn = sqlite3.connect("database")
		cursor = conn.cursor()
		remove = "DELETE FROM pacchetti WHERE packetID='"+packetID+"'"
		cursor.execute(remove)
		conn.commit()
		cursor.close()

	def getAllPeers(self):
		conn = sqlite3.connect("database")
		cursor = conn.cursor()

		select = "SELECT * FROM vicini"
		cursor.execute(select)
		results = cursor.fetchall()
		conn.commit()
		cursor.close()
		return results

	def getPacchetto(self , packetID):
		conn = sqlite3.connect("database")
		cursor = conn.cursor()

		select = "SELECT * FROM pacchetti WHERE packetID='"+packetID+"'"
		cursor.execute(select)
		result = cursor.fetchall()
		conn.commit()
		cursor.close()
		return result

	def getAllPacchetti(self):
		conn = sqlite3.connect("database")
		cursor = conn.cursor()

		select = "SELECT * FROM pacchetti"
		cursor.execute(select)
		results = cursor.fetchall()
		conn.commit()
		cursor.close()
		return results







