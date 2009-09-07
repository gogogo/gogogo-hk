# -*- coding: utf-8 -*-

from google.appengine.ext import db
from graphs import Graph , Node , Arc
from gogogo.models import *
from ragendja.dbutils import prefetch_references
import logging
from gogogo.models.loaders import ListLoader , FareStopLoader

class TransitGraph(Graph):
    """
    A graph built by transit information
    """

    def create():
        """
        Try to load a instance from memcache, if not found,
        it will create a new transit graph.
        """
        #TODO - Enable memcache
        graph = TransitGraph()
        graph.load()
        return graph
        
    create = staticmethod(create)

    def __init__(self):
        Graph.__init__(self)
        self.agency_table = {}
        self.stop_table = {}
        self.cluster_table = {}
        self.route_table = {}
        self.trip_table = {}
        
        # stop to cluster matching
        self.stop_to_cluster = {}
        
        # cluster's name to node id matching
        self.cluster_id = {}
        
    def get_node(self,key):
        """
        Override parent's get_node function. (Supported to search by 
        cluster name , key and instance)
        
        @param data The key
        
        @type data db.Key
        @type data int
        @type data basestring The key of cluster
        """
        if isinstance(key,int):
            id = key
        else:
            if isinstance(key,basestring):
                # The name of the cluster
                if isinstance(key,unicode): 
                    cluster = str(key)
                else:
                    cluster = key 
            elif isinstance(key,db.Key):
                cluster = key().id_or_name()
            else:
                cluster = key.key().id_or_name()
                
            id = self.cluster_id[cluster]
            
        return Graph.get_node(self,id)
        
    def get_node_by_stop(self,stop):
        if isinstance(stop,basestring):
           key = stop 
        elif isinstance(stop,db.Key()):
            key = stop.id_or_name()
        else:
            key = stop.key().id_or_name()
            
        return self.get_node(self.stop_to_cluster[key])
        
    def load(self):
        """
       Load graph from database
        """
        
        route_list = []
        agency_list = []
        cluster_list = []
        trip_list = []
        
        # TODO : Replace by ListLoader
        # For testing
        query = Agency.all().filter("no_service = " ,False)
        
        for agency in query:
            self.agency_table[agency.key().id_or_name()] = agency
            agency_list.append(agency)
        
        # TODO: Dump all route
        query = Route.all()
        for route in query:
            route_list.append(route)
            self.route_table[route.key().id_or_name() ] = route
            
        prefetch_references(route_list,"agency",agency_list)

        # TODO: Dump all trip
        query = Trip.all()
        for trip in query:
            trip_list.append(trip)
            self.trip_table[trip.key().id_or_name()] = trip
            
        prefetch_references(trip_list,"route",route_list)
        
        # Fetch all the database record make fewer DB access call than filter("agency  in")
        query = Stop.all()
        for stop in query:
            self.stop_table[stop.key().id_or_name()] = stop
        
        query = Cluster.all()
        for cluster in query:
            cluster_list.append(cluster)
            self.cluster_table[cluster.key().id_or_name()] = cluster
            node = Node(name = cluster.key().id_or_name() , data = cluster)
            self.cluster_id [cluster.key().id_or_name()] = self.add_node(node)
            #logging.info(cluster.key().id_or_name())
            
            for key in cluster.members:
                name = key.id_or_name()
                if name in self.stop_table:
                    self.stop_to_cluster[name] = cluster
        
        # Process agency with "free_transfer"
        for agency in agency_list:
            if agency.free_transfer:
                logging.info("Processing " +agency.key().id_or_name())
                query = db.GqlQuery("SELECT __key__ from gogogo_farestop WHERE agency = :1 and default = True limit 1"
                    ,agency)
                key = query.get()
                if key == None:
                    continue
                farestop_loader = FareStopLoader(key.id_or_name())
                farestop_loader.load()
                farestop = farestop_loader.get_farestop()
                
                pair_list = farestop_loader.get_pair_list()
                
                for pair in pair_list:        
                    a = self.get_node_by_stop(pair["from_stop"])
                    b = self.get_node_by_stop(pair["to_stop"])
                    
                    #TODO , don't save entity in graph , reduce the memory usage
                    arc = Arc(data = (agency,farestop) ,weight = pair["fare"] )
                    arc.link(a,b)
                    self.add_arc(arc)
        
        for trip in trip_list:           
            if trip.route.agency.free_transfer == True: 
                #Those trips are already processed in the previous block
                continue
                
            logging.info(trip.key().id_or_name())                
            cluster_group = {}
            
            for key in trip.stop_list:
                try:
                    to_stop = self.stop_table[key.id_or_name()]
                except KeyError:
                    logging.error( "Stop(%s) not found" % key.id_or_name())
                    continue
                
                cluster = self.stop_to_cluster[to_stop.key().id_or_name()]
                cluster_name = cluster.key().id_or_name()
                if cluster_name not in cluster_group: # ignore self-looping
                    
                    for from_cluster_name in cluster_group:
                        a  = self.get_node(from_cluster_name)
                        b  = self.get_node(cluster_name)
                        
                        # Ignore weight in testing phase
                        #TODO , don't save entity in graph , reduce the memory usage
                        arc = Arc(data= trip)
                        arc.link(a,b)
                        self.add_arc(arc)       
                    
                    cluster_group[cluster_name] = cluster;
                        

        
