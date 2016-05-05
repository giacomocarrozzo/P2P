# -*- coding: utf-8 -*-

#marcello 192.168.043.128|fe80:0000:0000:0000:7a31:c1ff:fecd:7dae - 172.030.014.003|fc00:0000:0000:0000:0000:0000:0014:0003
#enrico 192.168.043.196|fe80:0000:0000:0000:0226:b6ff:fe78:9cef - 172.030.014.001|fc00:0000:0000:0000:0000:0000:0014:0001
#giacomo 192.168.043.179|fe80:0000:0000:0000:8046:4bbd:91ca:b484 - 172.030.014.004|fc00:0000:0000:0000:0000:0000:0014:0004
#andrea 192.168.043.113|fe80:0000:0000:0000:d253:49ff:fece:9247 - 172.030.014.002|fc00:0000:0000:0000:0000:0000:0014:0002
#valerio 													    - 172.030.014.005|fc00:0000:0000:0000:0000:0000:0014:0005

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
