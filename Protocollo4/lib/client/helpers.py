# -*- coding: utf-8 -*-

from ..database import Table

class Files(Table):
	_fields = ["id", "name", "parts", "size", "status"] #randomid, nomefile, numeroparti, status del file (ce l'ho, non ce l'ho)

class Peers(Table):
	_fields = ["file", "ip", "port", "parts"]

class Parts(Table):
	_fields = ["file", "n"]
	
def db_init(db):
	db.define(Files)
	db.define(Peers)
	db.define(Parts)