#!/usr/bin/env python


import sqlite3 as sqlite

import json

from flask import Flask, request, make_response, jsonify, g

DATABASE = "debug.db"

app = Flask( __name__ )


lookups = {}




def socialdry_create_graph( db, name ):
	global lookups
	out = None
	if name in lookups["graphs"]:
		return None

	with db:
		cur = db.cursor()
		out = True
		cur.execute( "INSERT INTO graphs (name) VALUES (?)", (name,) )
	
	with db:
		cur = db.cursor()
		cur.execute( "SELECT id FROM graphs WHERE name = ?", (name,) )
		results = cur.fetchall()
		lookups["graphs"][name] = results[0][0]
		lookups["types"][name] = {}
		lookups["inverse-types"][name] = {}
		
	
	return out

def socialdry_create_node( db, graph, name, fields ):
	global lookups
	out = None
	
	if graph not in lookups["graphs"]:
		return None
	
	graph_id = lookups["graphs"][graph]
	
	new_fields = {}
	
	for key in fields:
		if key not in ["$id", "$created", "$name"]:
			new_fields[key] = fields[key];
	
	
	jfields = json.dumps( new_fields )
	with db:
		cur = db.cursor()
		cur.execute( "SELECT id FROM nodes WHERE graph = ? AND name = ?", (graph_id, name) )
		results = cur.fetchall()
		if len( results ) < 1:
			out = True
	
	if out:
		with db:
			cur = db.cursor()
			cur.execute( "INSERT INTO nodes (name, json, graph) VALUES (?, ?, ?)", (name, jfields, graph_id) )
		
		with db:
			cur = db.cursor()
			cur.execute( "SELECT id FROM nodes WHERE name = ? AND graph = ?", (name, graph_id) )
			results = cur.fetchall()
			out = results[0][0]
			
	
	return out

def socialdry_get_node_by_id( db, graph, node_id ):
	global lookups
	out = None
	
	if graph not in lookups["graphs"]:
		return None
	
	graph_id = lookups["graphs"][graph]
	
	with db:
		cur = db.cursor()
		cur.execute( "SELECT name, json, created FROM nodes WHERE id = ? AND graph = ?", (node_id, graph_id) )
		results = cur.fetchall()
		if len( results ) > 0:
			(name, jfields, created) = results[0]
			out = {}
			fields = json.loads(jfields)
			for (key, value) in fields.items():
				out[key] = value
			
			out["$id"] = node_id
			out["$name"] = name
			out["$created"] = created
	
	return out

def socialdry_get_node_by_name( db, graph, name ):
	global lookups
	out = None
	
	if graph not in lookups["graphs"]:
		return None
	
	graph_id = lookups["graphs"][graph]
	
	with db:
		cur = db.cursor()
		cur.execute( "SELECT id, json, created FROM nodes WHERE name = ? AND graph = ?", (name, graph_id) )
		results = cur.fetchall()
		if len( results ) > 0:
			(id, jfields, created) = results[0]
			out = {}
			
			fields = json.loads(jfields)
			for (key, value) in fields.items():
				out[key] = value
			
			out["$id"] = id
			out["$name"] = name
			out["$created"] = created
	
	return out

	
	

def socialdry_update_node_by_id( db, graph, node_id, fields ):
	global lookups
	out = None
	
	if graph not in lookups["graphs"]:
		return None
	
	graph_id = lookups["graphs"][graph]
	
	node = socialdry_get_node_by_id( db, graph, node_id )
	
	if not node:
		return None
	
	keys = node.keys()
	keys.remove( "$id" )
	keys.remove( "$name" )
	keys.remove( "$created" )
	
	all_fields = {}
	for key in keys:
		all_fields[key] = node[key]
	
	for (key, value) in fields.items():
		all_fields[key] = value
	
	with db:
		cur = db.cursor()
		jfields = json.dumps( all_fields )
		cur.execute( "UPDATE nodes SET json = ? WHERE id = ? AND graph = ?", (jfields, node["$id"], graph_id ) )
		out = True
	
	return out

def socialdry_update_node_by_name( db, graph, name, fields ):
	global lookups
	out = None
	
	if graph not in lookups["graphs"]:
		return None
	
	graph_id = lookups["graphs"][graph]
	
	node = socialdry_get_node_by_name( db, graph, name )
	
	if not node:
		return None
	
	keys = node.keys()
	keys.remove( "$id" )
	keys.remove( "$name" )
	keys.remove( "$created" )
	
	all_fields = {}
	for key in keys:
		all_fields[key] = node[key]
	
	for (key, value) in fields.items():
		all_fields[key] = value
	
	with db:
		cur = db.cursor()
		jfields = json.dumps( all_fields )
		cur.execute( "UPDATE nodes SET json = ? WHERE id = ? AND graph = ?", (jfields, node["$id"], graph_id ) )
		out = True
	
	return out

def socialdry_remove_graph( db, graph ):
	global lookups
	out = None
	
	if graph not in lookups["graphs"]:
		return None
	
	graph_id = lookups["graphs"][graph]
	
	del lookups["graphs"][graph]
	
	with db:
		cur = db.cursor()
		cur.execute( "DELETE FROM types WHERE graph = ?", (graph_id,) )
		cur.execute( "DELETE FROM edges WHERE graph = ?", (graph_id,) )
		cur.execute( "DELETE FROM nodes WHERE graph = ?", (graph_id,) )
		cur.execute( "DELETE FROM graphs WHERE id = ?", (graph_id,) )
	
	return True

def socialdry_remove_node_by_id( db, graph, node_id ):
	global lookups
	out = None
	
	if graph not in lookups["graphs"]:
		return None
	
	graph_id = lookups["graphs"][graph]
	
	with db:
		cur.execute( "DELETE FROM nodes WHERE id = ? AND graph = ?", (node_id, graph_id) )
		cur.execute( "DELETE FROM edges WHERE begin = ? AND graph = ?", (node_id, graph_id) )
		cur.execute( "DELETE FROM edges WHERE end = ? AND graph = ?", (node_id, graph_id) )
		
	
	return True


def socialdry_remove_node_by_name( db, graph, name ):
	global lookups
	out = None
	
	if graph not in lookups["graphs"]:
		return None
	
	graph_id = lookups["graphs"][graph]
	
	node = socialdry_get_node_by_name( db, graph, name )
	if not node:
		return None
	
	socialdry_remove_node_by_id( db, graph, node["$id"] )
		
	return True


def socialdry_create_edge_type( db, graph, edge_type ):
	global lookups
	
	
	if graph not in lookups["graphs"]:
		return None
	
	if edge_type in lookups["types"][graph]:
		return True
	
	graph_id = lookups["graphs"][graph]
	
	with db:
		cur = db.cursor()
		cur.execute( "INSERT INTO types (type_name, graph) VALUES (?, ?)", (edge_type, graph_id ) )
	
	with db:
		cur = db.cursor()
		cur.execute( "SELECT type_id FROM types WHERE type_name = ? AND graph = ?", (edge_type, graph_id ) )
		results = cur.fetchall()
		lookups["types"][graph][edge_type] = results[0][0]
		lookups["inverse-types"][graph][results[0][0]] = edge_type
	
	return True


def socialdry_create_edge_by_id( db, graph, begin, end, edge_type ):
	global lookups
	out = None
	
	if graph not in lookups["graphs"]:
		return None
	
	graph_id = lookups["graphs"][graph]
	
	type_id = 0
	if edge_type in lookups["types"][graph]:
		type_id = lookups["types"][graph][edge_type]
	else:
		type_id = socialdry_create_edge_type( db, graph, edge_type )
	
	with db:
		cur = db.cursor()
		cur.execute( "SELECT id FROM nodes WHERE id = ? AND graph = ?", (begin, graph_id) )
		results = cur.fetchall()
		if len( results ) > 0:
			print "DEBUG: begin found"
			cur.execute( "SELECT id FROM nodes WHERE id = ? AND graph = ?", (end, graph_id) )
			results = cur.fetchall()
			if len( results ) > 0:
				print "DEBUG: end found"
				cur.execute( "SELECT * FROM edges WHERE begin = ? AND end = ? AND type = ? AND graph = ?", (begin, end, type_id, graph_id) )
				results = cur.fetchall()
				if len( results ) < 1:
					cur.execute( "INSERT INTO edges (begin, end, type, weight, graph) VALUES( ?, ?, ?, 1.0, ? )", (begin, end, type_id, graph_id ) )
					out = True
	return out
				
	
def socialdry_create_edge_by_name( db, graph, begin, end, edge_type ):
	node_begin = socialdry_get_node_by_name( db, graph, begin )
	node_end = socialdry_get_node_by_name( db, graph, end )
	
	if node_begin and node_end:
		return socialdry_create_edge_by_id( db, graph, node_begin["$id"], end_begin["$id"], edge_type )
	
	return None

def socialdry_get_edges_by_id( db, graph, begin, edge_type ):
	global lookups
	out = None
	
	if graph not in lookups["graphs"]:
		return None
	
	graph_id = lookups["graphs"][graph]
	
	type_id = 0
	if edge_type in lookups["types"][graph]:
		type_id = lookups["types"][graph][edge_type]
	else:
		return []
	
	with db:
		cur = db.cursor()
		cur.execute( "SELECT end, weight, created FROM edges WHERE begin = ? AND type = ? AND graph = ?", (begin, type_id, graph_id ) )
		results = cur.fetchall()
		out = []
		for row in results:
			(end, weight, created) = row
			entry = {}
			entry["begin"] = begin
			entry["end"] = end
			entry["weight"] = weight
			entry["created"] = created
			entry["type"] = edge_type
			out.append( entry )
		
	return out

def socialdry_remove_edge_by_id( db, graph, begin, end, edge_type ):
	global lookups
	out = None
	
	if graph not in lookups["graphs"]:
		return None
	
	graph_id = lookups["graphs"][graph]
	
	type_id = 0
	if edge_type in lookups["types"][graph]:
		type_id = lookups["types"][graph][edge_type]
	else:
		return None
	
	with db:
		cur = db.cursor()
		cur.execute( "DELETE FROM edges WHERE begin = ? AND end = ? AND type = ? AND graph = ?", (begin, end, type_id, graph_id ) )
		out = True
	
	return out

def get_db():
	db = getattr( g, "_database", None )
	if not db:
		g._database = sqlite.connect( DATABASE )
		db = g._database
	
	return db


@app.teardown_appcontext
def close_connection(exception):
	db = getattr( g, "_database", None )
	if db:
		db.close()




@app.route( "/graphs", methods=["POST"] )
def create_graph():
	db = get_db()
	graph_name = request.form["name"]
	result = socialdry_create_graph( db, graph_name )
	return jsonify( result = result )

@app.route( "/graphs/<graph_name>", methods=["DELETE"] )
def remove_graph(graph_name):
	db = get_db()
	
	result = socialdry_remove_graph( db, graph_name )
	return jsonify( result = result )



@app.route( "/graphs/<graph_name>/nodes", methods=["POST"] )
def create_node( graph_name ):
	db = get_db()
	node_name = request.form["name"]
	fields = {}
	for key in request.form:
		fields[key] = request.form[key]
	
	del fields["name"]
	
	result = socialdry_create_node( db, graph_name, node_name, fields )
	
	return jsonify( result = result )

@app.route( "/graphs/<graph_name>/nodes/<int:node_id>", methods=["GET"] )
def get_node_by_id( graph_name, node_id ):
	db = get_db()
	node = socialdry_get_node_by_id( db, graph_name, node_id )
	return jsonify( node = node )

@app.route( "/graphs/<graph_name>/nodes", methods=["GET"] )
def get_node_by_name( graph_name ):
	db = get_db()
	
	node_name = request.args.get( "name", None )
	
	if not node_name:
		return jsonify( node = None )
	node = socialdry_get_node_by_name( db, graph_name, node_name )
	return jsonify( node = node )



@app.route( "/graphs/<graph_name>/nodes/<int:node_id>", methods=["PUT"] )
def update_node_by_id( graph_name, node_id ):
	db = get_db()
	fields = {}
	
	for key in request.form:
		fields[key] = request.form[key]
	
	node = socialdry_update_node_by_id( db, graph_name, node_id, fields )
	return jsonify( node = node )


@app.route( "/graphs/<graph_name>/nodes/<int:node_id>", methods=["DELETE"] )
def remove_node_by_id( graph_name, node_id ):
	db = get_db()
	result = socialdry_remove_node_by_id( db, graph_name, node_id )
	return jsonify( result = result )


@app.route( "/graphs/<graph_name>/edges", methods=["POST"] )
def create_edge_by_id( graph_name ):
	db = get_db()
	begin = int( request.form["begin"] )
	end = int(request.form["end"] )
	edge_type = request.form["type"]
	
	edge = socialdry_create_edge_by_id( db, graph_name, begin, end, edge_type )
	return jsonify( result = edge )



@app.route( "/graphs/<graph_name>/edges/<int:begin>", methods=["GET"] )
def get_edges_by_id( graph_name, begin ):
	db = get_db()
	edge_type = request.args.get( "type", None )
	backwards = request.args.get( "backwards", None )
	
	if not edge_type:
		return jsonify( edges = [] )
	
	edges = socialdry_get_edges_by_id( db, graph_name, begin, edge_type )
	return jsonify( edges = edges )
	
@app.route( "/graphs/<graph_name>/edges/<int:begin>", methods=["DELETE"] )
def remove_edges_by_id( graph_name, begin ):
	db = get_db()
	edge_type = request.args.get( "type", None )
	end = int(request.args.get( "end", None ))
	
	if not edge_type or not end:
		return jsonify( result = None )
	
	result = socialdry_remove_edge_by_id( db, graph_name, begin, end, edge_type )
	return jsonify( edges = edges )

@app.route( "/" )
def fetch_index():
	txt = ""
	with open( "index.html" ) as handle:
		txt = handle.read()
	
	return txt

@app.route( "/style.css" )
def fetch_style():
	txt = ""
	with open( "style.css" ) as handle:
		txt = handle.read()
	
	return txt

@app.route( "/code.js" )
def fetch_code():
	txt = ""
	with open( "code.js" ) as handle:
		txt = handle.read()
	
	return txt
	



db = sqlite.connect( "koe.db" )

with db:
	cur = db.cursor()

	cur.execute( "SELECT id, name FROM graphs" )
	results = cur.fetchall()
	lookups["graphs"] = {}
	lookups["inverse-graphs"] = {}
	
	for row in results:
		lookups["graphs"][row[1]] = row[0]
		lookups["inverse-graphs"][row[0]] = row[1]
	
	
	cur.execute( "SELECT type_id, type_name, graph FROM types" )
	results = cur.fetchall()
	lookups["types"] = {}
	lookups["inverse-types"] = {}
	for row in results:
		(type_id, type_name, graph_id) = row
		graph_name = lookups["inverse-graphs"][graph_id]
		if graph_name not in lookups["types"]:
			lookups["types"][graph_name] = {}
			lookups["inverse-types"][graph_name] = {}
		
		lookups["types"][graph_name][type_name] = type_id
		lookups["inverse-types"][graph_name][type_id] = type_name
		


if __name__ == "__main__":
	app.run( host = "0.0.0.0", debug = True )			
		
		


