from graphdb import GraphDB
import math

# Half of the fuel in km, used to generate graph connections
MAXIMUM_DISTANCE = 1000

# Class used to store aditional information for the brewery such as its coordinates and the beer name
class BeerAndCords:

    def __init__(self, beer=[], latitude="", longitude=""):
        self.beer = beer
        self.latitude = latitude
        self.longitude = longitude

    def set_coords(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

# Brewery class used to store brewery specific information extends BeerAndCords
class Brewery(BeerAndCords):

    def __init__(self, name="", brewery_id="", beer=[], latitude="", longitude=""):
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

"""
Stores search results
"""
class SearchResults:

    def __init__(self, factories=[], beer=[], distance=[0]):
        self.factories = factories
        self.beer = beer
        self.distance = distance

    def display_results(self):

        # Display total number of factories found
        print("Visited " + str(len(self.factories)) + " beer factories")

        # Display all factories that were visited
        for i in range(len(self.factories)):
            print("[" + self.factories[i].brewery_id + "] " + self.factories[i].name + " " + 
                str(self.factories[i].latitude) +  " " + str(self.factories[i].longitude) + " distance: " + str(self.distance[i]) + " km")

        # Display the total amount traveled
        print("Total distance: " + str(sum(self.distance)) + "\n")

        # Display total beer types collected
        print("Collected " + str(len(self.beer)) + " beer types")

        # Display all beer types
        for drink in self.beer:
            print(drink)

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
                    Create a new BeerAndCoords object if it donesn't exist
                    Store beer name in it 
                    Hash it by the brewery id
                    """
                    if line[1] in beer_and_coords:
                        beer_and_coords[line[1]].beer.append(line[2])
                    else:
                        beer_and_coords[line[1]] = BeerAndCords([line[2]])

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

        # Generates graph from Brewery objects
        self.generate_graph()

        # Stores generated graph into the database
        self.store_graph()

    def insert_home(self, latitude, longitude):

        # Creates Brewery object for home
        node_to_insert = Brewery(latitude=latitude, longitude=longitude, brewery_id="home")

        # stores connections
        connections = []

        nodes = self.database('db').contains(list)[0]

        for brewery_id in nodes:
            node = self.database(brewery_id).is_node(list)[0]
            # Calculate distance between two nodes
            distance = self.calculate_distance(node.latitude, node.longitude,
                    node_to_insert.latitude, node_to_insert.longitude)
 
            # If distance is equal or less to the maximum distance, store the connection
            if (distance <= MAXIMUM_DISTANCE):
                connections.append(Connection(node.brewery_id, distance))
        
        self.database.store_relation('home', 'is_node', node_to_insert)
        self.database.store_relation('home', 'connects', connections)

        self.database.commit()

    def remove_home(self):

        self.database.delete_relation('home', 'is_node')
        self.database.delete_relation('home', 'connects')

        self.database.commit()

    def find_min_neighbour(self, neighbours, visited):

        min_distance = MAXIMUM_DISTANCE+1
        min_neighbour = -1

        for neighbour in neighbours:
            if (neighbour.length < min_distance and neighbour.brewery_id not in visited):
                min_distance = neighbour.length
                min_neighbour = neighbour

        return min_neighbour

    def check_distance_to_home(self, node_to_check):
        home_node = self.database('home').is_node(list)[0]
        return self.calculate_distance(node_to_check.latitude, node_to_check.longitude, home_node.latitude, home_node.longitude)

    def nearest_neighbour(self, node_id, distance, visited, result):
        visited.append(node_id)

        neighbours = self.database(node_id).connects(list)[0]
        
        if (len(neighbours) == 0):
            return collected

        min_neighbour = self.find_min_neighbour(neighbours, visited)

        if (min_neighbour == -1):
            return collected

        distance_neighbour = min_neighbour.length

        # Retrieve Brewery object from the database
        min_neighbour = self.database(min_neighbour.brewery_id).is_node(list)[0]

        if (distance + distance_neighbour + self.check_distance_to_home(min_neighbour) <= MAXIMUM_DISTANCE * 2):

            # Update distance
            distance += distance_neighbour

            # Save data into results
            result.distance.append(distance_neighbour)
            result.factories.append(min_neighbour)
            result.beer = result.beer + min_neighbour.beer

            result = self.nearest_neighbour(min_neighbour.brewery_id, distance, visited, result)
        
        return result

    
    def find_path(self, latitude, longitude):

        # Crete home node and connect it with other nodes
        self.insert_home(latitude, longitude)

        # Retrieve home node
        home_node = self.database('home').is_node(list)[0]

        # Initilize the SearchResults object to store search results
        result = SearchResults()

        # Append home node to the begining of the results
        result.factories.append(home_node)
        
        # Find path using nearest neighbour algorithm
        result = self.nearest_neighbour('home', 0, [], result)

        # Retrieve last brewery
        last_node = result.factories[-1]

        # Append home node to the back
        result.factories.append(home_node)

        # Calculate the distance between home and the last node and append it
        result.distance.append(self.calculate_distance(latitude, longitude, last_node.latitude, last_node.longitude))

        # Remove home node and it's connections
        self.remove_home()

        return result

if __name__ == '__main__':
    graph = Graph('beer.db')

    result = graph.find_path(51.355468, 11.100790)

    # Display results
    result.display_results()

    # graph.generate_and_store_graph()

