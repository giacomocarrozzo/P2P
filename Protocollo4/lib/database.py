# -*- coding: utf-8 -*-

from threading import RLock

lock = RLock()

class Index(object):
	def __init__(self):
		self._data = dict()
	
	def __getitem__(self, value):
		return self._data.get(value, [])
	
	def push(self, value, rid):
		lock.acquire()
		if value not in self._data.iterkeys():
			self._data[value] = []
		self._data[value].append(rid)
		lock.release()
		
	def rem(self, rid):
		lock.acquire()
		for k in self._data.iterkeys():
			try:
				self._data[k].remove(rid)
			except:
				pass
		lock.release()

class Table(object):
	def __init__(self):
		self._rows = dict()
		self._indexes = dict()
		for fieldName in self._fields:
			self._indexes[fieldName] = Index()
			
	#def __getattr__(self, name):
	#	return self._fields.get(name)
	
	def __getitem__(self, name):
		return self._rows.get(name)
	
	def insert(self, **kwargs):
		newid = -1
		lock.acquire()
		try:
			newid = len(self._rows.keys())
			self._rows[newid] = kwargs
			for field, v in kwargs.items():
				self._indexes[field].push(v, newid)
		finally:
			lock.release()
		return newid
	
	def update(self, rid, **kwargs):
		lock.acquire()
		try:
			self._rows[rid].update(**kwargs)
			for field, v in kwargs.items():
				self._indexes[field].rem(rid)
				self._indexes[field].push(v, rid)
		finally:
			lock.release()
		
	def find_by(self, **kwargs):
		try:
			res = []
			rsets = []
			for field, val in kwargs.items():
				rsets.append(set(self._indexes[field][val]))
			rset = set.intersection(*rsets)
			for rid in rset:
				res.append((rid, self[rid]))
			return res
		except:
			return []
		
	def find_like(self, field, value):
		try:
			res = []
			for rid, rdata in self._rows.items():
				if value in rdata[field]:
					res.append((rid, rdata))
			return res
		except:
			return []
		
	def delete(self, rid):
		lock.acquire()
		try:
			del self._rows[rid]
			for field in self._fields:
				self._indexes[field].rem(rid)
		finally:
			lock.release()

class Database(object):
	def __init__(self):
		self._tables = dict()
		
	def __getattr__(self, name):
		return self._tables.get(name)
	
	def define(self, table):
		self._tables[table.__name__] = table()
	