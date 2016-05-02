# -*- coding: utf-8 -*-
#import time
from lib.client.base import Client
from lib.database import Database
from lib.client.helpers import db_init

HOST = "2001:0000:0000:0000:0000:0000:0000:000b"
TRACKER = ("2001:0000:0000:0000:0000:0000:0000:000b" , int(3000))

if __name__ == "__main__":
	db = Database()
	db_init(db)
	c = Client(HOST, TRACKER, db)
	try:
		c.login()
		while True:
			print "\n"
			print "################################"
			print "                               #"
			print "      #####  #####  #####      #"
			print "      #   #     ##  #   #      #"
			print "      #####    ##   #####      #"
			print "      #      ##     #          #"
			print "      #     #####   #          #"
			print "                               #"
			print "                               #"
			print "      MENU                     #"
			print "      1. ricerca               #"
			print "      2. select file           #"
			print "      3. select file           #"
			print "      4. logout                #"
			print "                               #"
			print "################################"
			print "\n"
			choice = raw_input("scegli: ")
			if choice == "1":
				to_search = raw_input("inserisci nome file: ")
				c.search(search=to_search)
			elif choice == "2":
				fchoice = raw_input("id: ")
				fparts = raw_input("parts: ")
				c.completeSearch(choice=fchoice, parts=fparts)
			elif choice == "3":
				fchoice = raw_input("id: ")
				c.enqueue_download(fchoice)
			elif choice == "4":
				c.logout()
	except KeyboardInterrupt:
		print "Quitting.."
		print c.threads
		for t in c.threads:
			print "stopping "+str(t)
			t.stop()
			t.join()
		#c._upman.shutdown()
	except Exception:
		print "SMTH VERY WRONG.."
	finally:
		print "Bye!"