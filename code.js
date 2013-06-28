
function Socialdry( graph, baseurl ){
	var self = this;
	this.baseurl = baseurl || "http://localhost:5000";
	this.graph = graph
	
	this.baseurl += "/graphs/" + this.graph;
	

	this.Node = function( content ){
		if( (typeof content) == "string" ){
			var name = content;
			content = {$name: name};
			}
		
		
		this.fields = content;
		this.id = content.$id || -1;
		this.created = content.$created || "";
		this.name = content.$name || "";
		this.edges = {};
		this.baseurl = self.baseurl;
		};
	
	this.Node.prototype.load = function(){
		var self = this;
			$.getJSON( self.baseurl + "/nodes/" + this.id, function(data){
				self.fields = data.node;
				self.name = data.node.$name;
				self.created = data.node.$created;
				
			});
		return self;
		}
	
	this.Node.prototype.save = function(){
		var self = this;
		var fields = this.fields;
		
		if( self.id >= 0 ){
			
			$.ajax({ url: this.baseurl + "/nodes/" + this.id, 
					 type: 'PUT',
					 data: fields
					});
			}
		// create new node
		else {
			fields.name = this.name;
			
			$.post( this.baseurl + "/nodes", fields, function(data){
				self.id = data.result;
				} );
			}
		
		}
	
	this.Node.prototype.connect = function( target, type ){
		var self = this;
		$.post( this.baseurl + "/edges", {begin: self.id, end: target.id, type: type}, function(response){console.log(response);} );
		}
	
	this.Node.prototype.fetchEdges = function(type){
		var self = this;
		var edgeType = type;
		
		$.getJSON( self.baseurl + "/edges/" + self.id + "?type=" + type, function(data){
				var edges = data.edges;
				console.log(edges);
				self.edges[edgeType] = [];
				for( var i = 0 ; i < edges.length ; i += 1 ){
					var edge = edges[i];
					
					var entry = {target: new self.constructor({$id: edge.end}), weight: edge.weight, created: edge.created};
					self.edges[edgeType].push( entry );
					}
			});
		return this.edges;
		}
	
	}


Socialdry.prototype.fetchNode = function( name ){
	var result = {};
	//result.node = {};
	var self = this;
	$.getJSON( this.baseurl + "/nodes?name=" + name, function(data){
		//result.node = data.node;
		result = new self.Node( data.node );
		});
		
	return result;
	}

$(document).ready(function(){
	jQuery.ajaxSetup({async:false});

/*	
	var sd = new Socialdry( "mauri" );
	
	var node = sd.fetchNode( "nauris" );
	
	console.log( node );
	
	node.load();
	
	//setTimeout( function(){ console.log(node); }, 3000 );
	node.fetchEdges("vihannes");
	node.edges.vihannes[0].target.load();
	
	console.log( node.edges.vihannes[0] );
	
	//node.fields.sukkapuikko = "kissakala";
	
	//node.save();
	
	
	//var uusi_node = new sd.Node( "debug-0" );
	
	//uusi_node.save();
	
	var node2 = sd.fetchNode( "debug-0" );
	
	//console.log( node2 );
	
	//node2.connect( node, "testing" );
	
	//node2.connect( node.edges.vihannes[0].target, "testing" );
	
	
	node2.fetchEdges( "testing" );
	
	console.log( node2.edges );
	*/
	
	
	});
