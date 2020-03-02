import math
import sys
import copy
import csv
import random

from graphdb import GraphDB

from connection import Connection
from brewery import Brewery
from beer_and_coords import BeerAndCoords
from search_results import SearchResults

# Stores the brewery graph
class Graph:

    def __init__(self, database_directory, nodes=[], connections={}, precalculated_distance={}, maximum_distance=1000, home_id="", weight=10):
        self.database = GraphDB(database_directory, autocommit=False)
        self.nodes = nodes
        self.connections = connections
        self.precalculated_distance = precalculated_distance
        self.maximum_distance = maximum_distance
        self.home_id = home_id
        self.weight = weight

    def reset(self):

        """
        Resets graph object to default value

        >>> graph = Graph('', nodes=[0], connections={'test' : ''}, precalculated_distance={ 'test' : 0 }, maximum_distance=100)
        >>> graph.reset()
        >>> graph.nodes == [] and graph.connections == {} and graph.precalculated_distance == {} and graph.maximum_distance == 1000
        True
        """

        self.nodes = []
        self.connections = {}
        self.precalculated_distance = {}
        self.maximum_distance = 1000

    def calculate_distance(self, lat1, lon1, lat2, lon2):

        """
        Calculates the distance beween two coordinates

        >>> Graph.calculate_distance(Graph, 51, 12, 58, 3)
        969.648
        >>> Graph.calculate_distance(Graph, 34, 2, 31, 10)
        820.731
        """
      
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
        """
        Parses input files and generates nodes for the graph
        """

        beer_and_coords = {}
        breweries = []

        # Read geocodes.csv file
        with open('./data/geocodes.csv', encoding='utf8') as coord_data:
            csv_reader = csv.reader(coord_data, delimiter=',')
            for row in csv_reader:

                #Check if no data is missing 
                if (len(row) >= 4):

                    # Create new BeerAndCoords object and hash it using brewery id as the key
                    beer_and_coords[row[1]] = BeerAndCoords(latitude=row[2], longitude=row[3])

        # Read beers.csv file
        with open('./data/beers.csv', encoding='utf8') as beer_data:
            csv_reader = csv.reader(beer_data, delimiter=',')
            for row in csv_reader:

                # Check if no data is missing
                if (len(row) >= 3):

                    # Check if the beer is in the beer_and_coords array
                    if row[1] in beer_and_coords:

                        # Append the beer to the beer_and_coords' beer array by the brewery id
                        beer_and_coords[row[1]].beer.append(row[2])

        # Read breweries.csv file
        with open('./data/breweries.csv', encoding='utf8') as brewery_data:
            csv_reader = csv.reader(brewery_data, delimiter=',')
            for row in csv_reader:

                """
                Check if no data is missing
                Check BeerAndCoords object is hashed in the beer_and_coords dictionary by brewery id
                Check if latitude is set
                """
                if (len(row) >= 2 and row[0] in beer_and_coords and beer_and_coords[row[0]].latitude != ""):

                    # Retrieve BeerAndCoords object by brewery id
                    temp_beer_and_coords = beer_and_coords[row[0]]

                    # Initialise temporary Brewery object
                    temp_brewery = Brewery(row[1], row[0], temp_beer_and_coords.beer, float(temp_beer_and_coords.latitude), float(temp_beer_and_coords.longitude))

                    # Append to all breweries
                    breweries.append(temp_brewery)

        self.nodes = breweries

    def generate_graph(self):
        """
        Generates graph from nodes

        >>> graph = Graph('')
        >>> graph.reset()
        >>> graph.nodes = [Brewery(brewery_id='1', latitude=34, longitude=2),
        ...     Brewery(brewery_id='2', latitude=34, longitude=14),
        ...     Brewery(brewery_id='3', latitude=40, longitude=10)]
        >>> graph.generate_graph()
        >>> for key in graph.connections:
        ...     for connection in graph.connections[key]:
        ...         print(connection.brewery_id)
        3
        3
        1
        2
        """
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

                if (final_key in self.precalculated_distance):
                    distance = self.precalculated_distance[final_key]

                else:

                    # Calculate distance between two nodes
                    distance = self.calculate_distance(node.latitude, node.longitude,
                            temp_node.latitude, temp_node.longitude)

                    # Store the value
                    self.precalculated_distance[final_key] = distance

                # If distance is equal or less to the maximum distance, store the connection
                if (distance <= self.maximum_distance):
                    connections.append(Connection(temp_node.brewery_id, distance))

            # Hash connections using brewery id as a key
            self.connections[node.brewery_id] = connections

    def store_graph(self):
        """
        Stores graph in the database

        >>> graph = Graph('test.db')
        >>> graph.reset()
        >>> graph.nodes = [Brewery(brewery_id='1', latitude=34, longitude=2),
        ...     Brewery(brewery_id='2', latitude=34, longitude=14),
        ...     Brewery(brewery_id='3', latitude=40, longitude=10)]
        >>> graph.generate_graph()
        >>> graph.store_graph()
        >>> graph.database('db').contains(list)[0]
        ['1', '2', '3']
        >>> for i in range(3):
        ...     print(len(graph.database(''+str(i+1)).is_node(list)))
        1
        1
        1
        >>> for i in range(3):
        ...     for element in graph.database(''+str(i+1)).connects(list)[0]:
        ...         print(element.brewery_id)
        3
        3
        1
        2
        >>> graph.database._destroy()
        """

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

        """
        Create home node and insert it into the database
        >>> graph = Graph('test.db', home_id='home')
        >>> graph.reset()
        >>> graph.insert_home(51, 53)
        >>> graph.database(graph.home_id).is_node(list)[0].latitude
        51
        >>> graph.database._destroy()
        """

        # Creates Brewery object for home
        node_to_insert = Brewery(latitude=latitude, longitude=longitude, brewery_id="home")

        # stores connections
        connections = []

        nodes = self.database('db').contains(list)

        if (len(nodes) == 0):
            nodes = []
        else:
            nodes = nodes[0]
        
        for brewery_id in nodes:
            
            node = self.database(brewery_id).is_node(list)[0]

            # Calculate distance between two nodes
            distance = self.calculate_distance(node.latitude, node.longitude,
                    node_to_insert.latitude, node_to_insert.longitude)
 
            # If distance is equal or less to the maximum distance, store the connection
            if (distance <= self.maximum_distance):
                connections.append(Connection(node.brewery_id, distance))
        
        self.database.store_relation(self.home_id, 'is_node', node_to_insert)
        self.database.store_relation(self.home_id, 'connects', connections)

        self.database.commit()

    def remove_home(self):

        """
        Removes home node

        >>> graph = Graph('test.db', home_id='home')
        >>> graph.insert_home(51, 14)
        >>> graph.remove_home()
        >>> len(graph.database(graph.home_id).is_node(list))
        0
        >>> graph.database._destroy()
        """

        self.database.delete_item(self.home_id)

        self.database.commit()

    def find_min_neighbour(self, neighbours, visited):

        """
        Find the closest neighbour that wasn't already visited

        >>> graph = Graph('')
        >>> graph.reset()
        >>> min_neighbour = graph.find_min_neighbour([Connection('2', 3), Connection('123', 7.89), Connection('3', 0.1)], ['3', '14'])
        >>> min_neighbour.brewery_id
        '2'
        """

        min_distance = self.maximum_distance+1
        min_neighbour = -1

        for neighbour in neighbours:

            neighbour_node = self.database(neighbour.brewery_id).is_node(list)[0]

            # Check if neighbour is closer than the previous ones and is not already visited and apply the weight
            if (neighbour.length - len(neighbour_node.beer) * self.weight < min_distance and neighbour.brewery_id not in visited):

                #Store it
                min_distance = neighbour.length
                min_neighbour = neighbour

        return min_neighbour

    def check_distance_to_home(self, node_to_check):

        """
        Find the distance between the home node and the specified node

        >>> graph = Graph('test.db')
        >>> graph.reset()
        >>> graph.insert_home(51, 14)
        >>> node_to_test = Brewery(latitude=41, longitude=7)
        >>> graph.check_distance_to_home(node_to_test)
        1235.096
        >>> graph.database._destroy()
        """

        # Retrieve home node from the database
        home_node = self.database(self.home_id).is_node(list)[0]

        return self.calculate_distance(node_to_check.latitude, node_to_check.longitude, home_node.latitude, home_node.longitude)

    def find_max_result(self, results):
        """
        Find the maximum number of beers collected
        """

        # sets initial values
        maximum_beer = 0
        max_result = 0

        # repeats for the length of results
        for i in range(len(results)):

            # finds out the amount of beer collected
            amount_of_beer = len(results[i].beer)

            # gets the sum of all distances
            distance_sum = sum(results[i].distance)
            
            # if distance sum is less than the fuel of the aircraft and the number of beer collected is more then the previous maximum
            if (distance_sum <= self.maximum_distance * 2 and amount_of_beer > maximum_beer):

                # updates the maximum number of beer collected and the maximum result
                maximum_beer = amount_of_beer
                max_result = i

        return results[max_result]


    def nearest_neighbour(self, node_id, distance, visited, results):

        """
        Generates the path using the neares neighboar algorithm


        >>> graph = Graph('test.db', home_id='home')
        >>> graph.reset()
        >>> graph.nodes = [Brewery(brewery_id='1', latitude=34, longitude=2),
        ...     Brewery(brewery_id='2', latitude=34, longitude=14),
        ...     Brewery(brewery_id='3', latitude=31, longitude=10)]
        >>> graph.generate_graph()
        >>> graph.store_graph()
        >>> graph.insert_home(35, 2)
        >>> result = SearchResults()
        >>> result = graph.nearest_neighbour(graph.home_id, 0, [], [result])
        >>> result.return_in_json()
        '{"breweries": [{"name": "", "id": "1", "lat": 34, "long": 2}, {"name": "", "id": "3", "lat": 31, "long": 10}], "beer": [], "distance": [0, 111.195, 820.731, 868.121]}'
        >>> graph.database._destroy()
        """

        if (distance >= self.maximum_distance * 2):
            results[-1].distance.append(self.check_distance_to_home(results[-1].factories[-1]))
            return self.find_max_result(results)

        # Add node to the visited list
        visited.append(node_id)

        # Get neightbours
        neighbours = self.database(node_id).connects(list)[0]

        
        # If no neighbours, return
        if (len(neighbours) == 0):
            results[-1].distance.append(self.check_distance_to_home(results[-1].factories[-1]))
            return self.find_max_result(results)

        # Find the closest neighbourcd
        min_neighbour = self.find_min_neighbour(neighbours, visited)

        # If it doesn't exist, return
        if (min_neighbour == -1):
            results[-1].distance.append(self.check_distance_to_home(results[-1].factories[-1]))
            return self.find_max_result(results)

        distance_neighbour = min_neighbour.length

        # Retrieve Brewery object from the database
        min_neighbour = self.database(min_neighbour.brewery_id).is_node(list)[0]

        if (distance + distance_neighbour + self.check_distance_to_home(min_neighbour) > self.maximum_distance * 2):
            results.append(copy.deepcopy(results[-1]))
            results[-2].distance.append(self.check_distance_to_home(results[-2].factories[-1]))

        # Update distance
        distance += distance_neighbour

        # Save data into results
        results[-1].distance.append(distance_neighbour)
        results[-1].factories.append(min_neighbour)
        results[-1].beer = results[-1].beer + min_neighbour.beer

        result = self.nearest_neighbour(min_neighbour.brewery_id, distance, visited, results)
        
        return result
    
    def find_path(self, latitude, longitude):

        # Create home node and connect it with other nodes
        self.insert_home(latitude, longitude)

        # Retrieve home node
        home_node = self.database(self.home_id).is_node(list)[0]

        # Initilize the SearchResults object to store search results
        result = SearchResults()

        # After the reinitilization the old value of the object is kept, so it is reset
        result.reset()

        # Append home node to the begining of the results
        result.factories.append(home_node)
        
        # Find path using nearest neighbour algorithm
        result = self.nearest_neighbour(self.home_id, 0, [], [result])

        # Retrieve last brewery
        last_node = result.factories[-1]

        # Append home node to the back
        result.factories.append(home_node)

        # Remove home node and it's connections
        self.remove_home()

        return result

    def genetic_near_neighbour(self, number_of_runs, latitude, longitude):

        """
        Runs genetic algorithm for nearest neigbour algorithm
        """

        # Creates SearchResults object to store the final result
        final_result = SearchResults()
        final_result.reset()

        # Sets the initial values
        max_number_of_beer = 0
        org_weight = 10
        new_weight = 10

        # Runs the genetic algorithm number_or_runs times
        for i in range(number_of_runs):

            # sets the weight to the mutated one
            self.weight = new_weight

            # Runs the neares neighbour algorithm with a mutated weight
            temp_result = self.find_path(latitude, longitude)

            # Checks if more beers were found than previous maximum
            if (len(temp_result.beer) > max_number_of_beer):
                
                # sets the maximum number of beer to the new maximum
                max_number_of_beer = len(temp_result.beer)

                # sets the orginal best weight to the new weight
                org_weight = new_weight

                # Updates the final result
                final_result = temp_result
            else:

                # resets the weith
                new_weight = org_weight

            # Decides if to add or subtract the mutation
            is_negative = random.randint(0, 1)

            if (is_negative == 1):

                # Generates mutation and substrcts it
                new_weight -= random.random() * 10
            else:

                # Generates mutation and adds it
                new_weight += random.random() * 10


        return final_result


if __name__ == '__main__':
    if (len(sys.argv) > 1 and sys.argv[1] == '-r'):
        GraphDB('beer.db')._destroy()
        graph = Graph('beer.db')
        graph.generate_and_store_graph()
    else:
        import doctest
        doctest.testmod()
    