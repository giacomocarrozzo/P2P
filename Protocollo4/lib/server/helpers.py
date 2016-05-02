# -*- coding: utf-8 -*-

from ..database import Table

class Sessions(Table):
	_fields = ["id", "ip", "port"]
	
class Files(Table):
	_fields = ["id", "name", "size", "psize"]
	
class Parts(Table):
	_fields = ["file", "session", "n"]

def db_init(db):
	db.define(Sessions)
	db.define(Files)
	db.define(Parts)
