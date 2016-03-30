import sqlite3
import time
import os.path
import threading
import sys

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
			self.app.log("about to initialize db")
			conn = sqlite3.connect('database')
			cursor = conn.cursor()

			c_str = '''CREATE TABLE vicini (ip TEXT, port INT)'''
			cursor.execute(c_str)
			c_str = '''CREATE TABLE pacchetti (packetID TEXT NOT NULL, time INT NOT NULL, peer_ip TEXT , peer_port INT)'''
			cursor.execute(c_str)
			c_str = '''CREATE TABLE files (filename TEXT NOT NULL, md5 TEXT NOT NULL)'''
			cursor.execute(c_str)

			conn.commit()
			cursor.close()
		except:
			self.app.log("error in initialize db ", "ERR")
			self.app.log(sys.exc_info()[0], "ERR")
			self.app.log(sys.exc_info()[1], "ERR")
			self.app.log(sys.exc_info()[2], "ERR")
			return

	def __init__(self, app):

		self.app = app
		self.dbControl = DBControl()
		self.dbControl.start()
		if not os.path.isfile('database'):
			self.initializeDatabase()
    	
	def stop(self):
		self.dbControl.stop()

	def insertPeer(self, indirizzo, port):
		conn = sqlite3.connect('database')
		cursor = conn.cursor()
		ip = str(indirizzo).lower()
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

		select = "SELECT * FROM files WHERE UPPER(filename) LIKE UPPER('%"+filename+"%')"
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
		self.app.log("retrieving all peers")
		conn = sqlite3.connect("database")
		cursor = conn.cursor()

		select = "SELECT * FROM vicini"
		cursor.execute(select)
		results = cursor.fetchall()
		print(results)
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







