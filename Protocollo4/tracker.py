# -*- coding: utf-8 -*-

import sys
from lib.server.base import Server
from lib.database import Database
from lib.server.handler import Handler
from lib.server.helpers import db_init

def get_ip():
	from netifaces import interfaces, ifaddresses, AF_INET6
	ip_list = []
	for interface in interfaces():
		for link in ifaddresses(interface)[AF_INET6]:
			ip_list.append(link['addr'])
	return ip_list

#HOST = "0000:0000:0000:0000:0000:0000:0000:0001"
#PORT = 3000
HOST = "2001:0000:0000:0000:0000:0000:0000:000b"
PORT = 3000

if __name__ == "__main__":
	print "ZenTorrent starting.."
	## HOST = get_ip()[0]
	db = Database()
	db_init(db)
	handler = Handler(db)
	server = Server((HOST, PORT), handler)
	# terminate with Ctrl-C
	try:
		print "Serving.."
		server.serve_forever()
	except KeyboardInterrupt:
		server.shutdown()
		sys.exit(0)