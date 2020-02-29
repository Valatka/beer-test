from graphdb import GraphDB
import math

# Half of the fuel in km, used to generate graph connections
MAXIMUM_DISTANCE = 1000

# Class used to store aditional information for the brewery such as its coordinates and the beer name
class BeerAndCords:

    def __init__(self, beer, latitude="", longitude=""):
        self.beer = beer
        self.latitude = latitude
        self.longitude = longitude

    def set_coords(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

# Brewery class used to store brewery specific information extends BeerAndCords
class Brewery(BeerAndCords):

    def __init__(self, name="", brewery_id="", beer="", latitude="", longitude=""):
        super().__init__(beer, latitude, longitude)
        self.name = name
        self.brewery_id = brewery_id

"""
Stores connections for nodes, before storing them into the database, 
so the final Brewery objects aren't holding the information themselves, 
because it is going to be handled by the the database
"""
class Connection:

    def __init__(self, brewery_id, length):
        self.brewery_id = brewery_id
        self.length = length

# Stores the brewery graph
class Graph:

    def __init__(self, database_directory, nodes=[], connections={}, precaulculated_distance={}):
        self.database = GraphDB(database_directory, autocommit=False)
        self.nodes = nodes
        self.connections = connections
        self.precaulculated_distance = precaulculated_distance

    def calculate_distance(self, lat1, lon1, lat2, lon2): 
      
        # Calculate distance between latitudes and longitutdes
        latitude_distance = math.radians(lat2 - lat1)
        longitude_distance = math.radians(lon2 - lon1)
      
        # Convert to radians
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)
        
        # earth's mean radius
        r = 6371

        # Apply harvesine formula
        a = (pow(math.sin(latitude_distance / 2), 2) + 
             pow(math.sin(longitude_distance / 2), 2) * 
                 math.cos(lat1) * math.cos(lat2))
        
        c = 2 * math.asin(math.sqrt(a))

        return round(r * c, 3)

    def generate_nodes(self):

        beer_and_coords = {}
        breweries = []

        # Read beers.csv file
        with open('./data/beers.csv', encoding='utf8') as beer_data:
            line = beer_data.readline()
            while (len(line) > 0):
                line = line.split(',')

                # Check if no data is missing
                if (len(line) >= 3):

                    """
                    Create a new BeerAndCoords object
                    Store beer name in it 
                    Hash it by the brewery id
                    """
                    beer_and_coords[line[1]] = BeerAndCords(line[2])
                line = beer_data.readline()

        # Read geocodes.csv file
        with open('./data/geocodes.csv', encoding='utf8') as coord_data:
            line = coord_data.readline()
            while (len(line) > 0):
                line = line.split(',')

                """
                Check if no data is missing 
                Check BeerAndCoords object is hashed in the beer_and_coords dictionary by brewery id
                """
                if (len(line) >= 4 and line[1] in beer_and_coords):

                    # Select BeerAndCoords object by brewery id and set the cordinates
                    beer_and_coords[line[1]].set_coords(line[2], line[3])
                line = coord_data.readline()

        # Read breweries.csv file
        with open('./data/breweries.csv', encoding='utf8') as brewery_data:
            line = brewery_data.readline()
            while (len(line) > 0):
                line = line.split(',')

                """
                Check if no data is missing
                Check BeerAndCoords object is hashed in the beer_and_coords dictionary by brewery id
                Latitude is set
                """
                if (len(line) >= 2 and line[0] in beer_and_coords and beer_and_coords[line[0]].latitude != ""):

                    # Retrieve BeerAndCoords object by brewery id
                    temp_beer_and_coords = beer_and_coords[line[0]]

                    # Initialise temporary Brewery object
                    temp_brewery = Brewery(line[1], line[0], temp_beer_and_coords.beer, float(temp_beer_and_coords.latitude), float(temp_beer_and_coords.longitude))

                    # Append to all breweries
                    breweries.append(temp_brewery)
                line = brewery_data.readline()

        self.nodes = breweries

    def generate_graph(self):

        # Loop through all nodes
        for primary in range(len(self.nodes)):

            # Array to store connection objects
            connections = []

            node = self.nodes[primary]

            # Loop through all nodes
            for secondary in range(len(self.nodes)):

                # Make sure that node doesn't connect to itself
                if (primary == secondary):
                    continue

                temp_node = self.nodes[secondary]

                # Check if distance was already calculated
                key = int(node.brewery_id)
                key_temp = int(temp_node.brewery_id)

                final_key = str(min(key, key_temp))+'|'+str(max(key, key_temp))

                if (final_key in self.precaulculated_distance):
                    distance = self.precaulculated_distance[final_key]

                else:

                    # Calculate distance between two nodes
                    distance = self.calculate_distance(node.latitude, node.longitude,
                            temp_node.latitude, temp_node.longitude)

                    # Store the value
                    self.precaulculated_distance[final_key] = distance

                # If distance is equal or less to the maximum distance, store the connection
                if (distance <= MAXIMUM_DISTANCE):
                    connections.append(Connection(temp_node.brewery_id, distance))

            # Hash connections using brewery id as a key
            self.connections[node.brewery_id] = connections

    def store_graph(self):
        brewery_ids = []
        for node in self.nodes:

            # Store brewery id
            brewery_ids.append(node.brewery_id)

            # Map brewery id to object
            self.database.store_relation(node.brewery_id, 'is_node', node)

            # Map brewery id to list of Connection objects
            self.database.store_relation(node.brewery_id, 'connects', self.connections[node.brewery_id])
        
        # Store of brewery ids for easier traversal of the graph
        self.database.store_relation('db', 'contains', brewery_ids)

        self.database.commit()

    def generate_and_store_graph(self):

        # Reads .csv files containing information and generates nodes
        self.generate_nodes()

        # Generates nodes from Brewery objects
        self.generate_graph()

        # Stores generated graph into the database
        self.store_graph()

    def insert_home(self, latitude, longitude):

        # Creates Brewery object for home
        node_to_insert = Brewery(latitude=latitude, longitude=longitude, brewery_id="home")

        # stores connections
        connections = []

        for node in self.nodes:

            # Calculate distance between two nodes
            distance = self.calculate_distance(node.latitude, node.longitude,
                    node_to_insert.latitude, node_to_insert.longitude)

            # If distance is equal or less to the maximum distance, store the connection
            if (distance <= MAXIMUM_DISTANCE):
                connections.append(Connection(node.brewery_id, distance))

        self.database.store_relation('home', 'is_node', node_to_insert)
        self.database.store_relation('home', 'connects', connections)

        self.commit()


if __name__ == '__main__':
    graph = Graph('beer.db')
    # graph.generate_and_store_graph()

