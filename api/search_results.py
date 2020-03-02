import json

"""
Stores search results
"""
class SearchResults:

    def __init__(self, factories=[], beer=set(), distance=[0]):
        self.factories = factories
        self.beer = beer
        self.distance = distance

    def reset(self):

        """
        Resets object to default values
        
        >>> result = SearchResults([Brewery('test_1', '1', ['test_1_beer'], 51, 14), Brewery('test_2', '2', ['test_2_beer'], 43, 5)], 
        ... ['test_1_beer', 'test_2_beer'], 
        ... [12, 34])
        >>> result.reset()
        >>> result.factories == [] and result.beer == [] and result.distance == [0]
        True

        """
        self.factories = []
        self.beer = set()
        self.distance = [0]

    def return_in_json(self):

        """
        Returns data in json format

        >>> result = SearchResults([Brewery('test_1', '1', ['test_1_beer'], 51, 14), Brewery('test_2', '2', ['test_2_beer'], 43, 5)], 
        ... ['test_1_beer', 'test_2_beer'], 
        ... [12, 34])
        >>> result.return_in_json()
        '{"breweries": [{"name": "test_1", "id": "1", "lat": 51, "long": 14}, {"name": "test_2", "id": "2", "lat": 43, "long": 5}], "beer": ["test_1_beer", "test_2_beer"], "distance": [12, 34]}'
        """

        results = {'breweries' : [], 'beer' : list(self.beer), 'distance' : self.distance}

        for factory in self.factories:

            results['breweries'].append({
                    'name' : factory.name,
                    'id' : factory.brewery_id,
                    'lat' : factory.latitude,
                    'long' : factory.longitude
                })

        return json.dumps(results)

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

if __name__ == '__main__':
    import doctest
    from brewery import Brewery
    doctest.testmod()