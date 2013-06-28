#!/usr/bin/env python

import sqlite3 as sqlite


import sys


db = sqlite.connect( sys.argv[1] )


with db:
	cur = db.cursor()
	
	cur.execute( "CREATE TABLE graphs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)" )
	cur.execute( "CREATE TABLE nodes  (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, json TEXT, created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, graph INTEGER)" )
	cur.execute( "CREATE TABLE edges  (begin INTEGER, end INTEGER, type INTEGER, weight REAL, created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, graph INTEGER)" )
	cur.execute( "CREATE TABLE types  (type_id INTEGER PRIMARY KEY, type_name TEXT, graph INTEGER)" ) 
