#!/usr/bin/env python

import requests


class Socialdry(object):
	def __init__( self, url = "http://localhost:5000" ):
		self.url = url
		self.graph = None
	
	def create_graph( self, name ):
		r = requests.post( self.url + "/graphs", data = {"name": name} )
		
		response = r.json()
		if response["result"]:
			self.graph = name
		
		return response

	def select_graph( self, graph ):
		self.graph = graph
	
	def remove_graph( self):
		r = requests.delete( self.url + "/graphs/" + self.graph )
		return r.json()
	
	def create_node( self, name, fields = {} ):
		url = self.url + "/graphs/" + self.graph + "/nodes" 
		data = {"name": name}
		for (key, value) in fields.items():
			data[key] = value
		r = requests.post( url, data = data )
		
		return r.json()
	
	def get_node( self, name ):
		url = self.url + "/graphs/" + self.graph + "/nodes" 
		if isinstance( name, int ):
			url += "/" + str(name)
			return requests.get( url ).json()
		else:
			return requests.get( url, params = {"name": name } ).json()
	
	def update_node( self, name, fields ):
		url = self.url + "/graphs/" + self.graph + "/nodes" 
		r = None
		if isinstance( name, int ):
			url += "/" + str(name)
			data = {}
			for (key, value) in fields.items():
				data[key] = value
			
			r = requests.put( url, data = data )
		else:
			data = {}
			for (key, value) in fields.items():
				data[key] = value
			r = requests.put( url, data = data, params = {"name": name } )
		
		return r.json()
	
	def remove_node( self, node_id ):
		url = self.url + "/graphs/" + self.graph + "/nodes/" + str(node_id)
		
		r = requests.delete( url )
		return r.json()
	
	def connect_nodes( self, begin_id, end_id, edge_type ):
		url = self.url + "/graphs/" + self.graph + "/edges"
		
		data = {"begin": begin_id, "end": end_id, "type": edge_type }
		
		r = requests.post( url, data = data )
		
		return r.json()
	
	def disconnect_nodes( self, begin_id, end_id, edge_type ):
		url = self.url + "/graphs/" + self.graph + "/edges/" + str( begin_id )
		
		r = requests.delete( url, params = {"end": end_id, "type": edge_type } )
		
		return r.json()
	
	def get_edges( self, begin_id, edge_type ):
		url = self.url + "/graphs/" + self.graph + "/edges/" + str( begin_id )
		
		r = requests.get( url, params = {"type": edge_type } )
		
		return r.json()




# Esimerkki
#sd = Socialdry()
#
#sd.create_graph( "mauri" )
#sd.select_graph( "mauri" )
#
#sd.create_node( "nauris", {"kolme": 4} )
#
#nauris = sd.get_node( "nauris" )["node"]
#print nauris
#
#sd.update_node( nauris["$id"], {"kolme": 1337, "joo": "jaa" } )
#
#nauris = sd.get_node( "nauris" )["node"]
#print nauris
#
#porkkana_id = sd.create_node( "porkkana", {} )["result"]
#
#print "porkkana_id", porkkana_id
#sd.connect_nodes( nauris["$id"], porkkana_id, "vihannes" )
#
#print sd.get_edges( nauris["$id"], "vihannes" )
#
#sd.remove_graph()


