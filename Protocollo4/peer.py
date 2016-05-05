# -*- coding: utf-8 -*-
#import time

#marcello 192.168.043.128|fe80:0000:0000:0000:7a31:c1ff:fecd:7dae - 172.030.014.003|fc00:0000:0000:0000:0000:0000:0014:0003
#enrico 192.168.043.196|fe80:0000:0000:0000:0226:b6ff:fe78:9cef - 172.030.014.001|fc00:0000:0000:0000:0000:0000:0014:0001
#giacomo 192.168.043.179|fe80:0000:0000:0000:8046:4bbd:91ca:b484 - 172.030.014.004|fc00:0000:0000:0000:0000:0000:0014:0004
#andrea 192.168.043.113|fe80:0000:0000:0000:d253:49ff:fece:9247 - 172.030.014.002|fc00:0000:0000:0000:0000:0000:0014:0002
#valerio 													    - 172.030.014.005|fc00:0000:0000:0000:0000:0000:0014:0005

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
