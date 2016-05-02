# -*- coding: utf-8 -*-

import socket
from SocketServer import ThreadingMixIn, TCPServer, BaseRequestHandler

class ServerHandler(BaseRequestHandler):

	def handle(self):
		
		print "SingleTCPHandler::handle()"
		
		reply = self.server._handler.handle(self.request)
		
		"""
		# self.request is the client connection
		data = self.request.recv(1024)  # clip input at 1Kb
		print "handle(): Received data : data =>\n[%s]" % (data)

		reply = data[::-1]
		"""

		print "handle(): Sending reply [%s]" % (reply)

		if reply is not None:
			self.request.sendall(reply)
		self.request.close()


class Server(ThreadingMixIn, TCPServer):
	daemonize = True
	allow_reuse_address = True
	address_family = socket.AF_INET6
	
	def __init__(self, server_address, handler):
		self._handler = handler
		TCPServer.__init__(self, server_address, ServerHandler)
		
	#def server_bind(self):
	#	self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, False)
	#	TCPServer.server_bind(self)
	