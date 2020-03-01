import json

"""
Stores search results
"""
class SearchResults:

    def __init__(self, factories=[], beer=[], distance=[0]):
        self.factories = factories
        self.beer = beer
        self.distance = distance

    def reset(self):
        self.factories = []
        self.beer = []
        self.distance =[0]

    def return_in_json(self):

        results = {'breweries' : [], 'beer' : self.beer, 'distance' : self.distance}

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
