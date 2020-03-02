import copy

# Class used to store aditional information for the brewery such as its coordinates and the beer name
class BeerAndCoords:

    def __init__(self, beer=[], latitude="", longitude=""):
        self.beer = copy.deepcopy(beer)
        self.latitude = latitude
        self.longitude = longitude

    def set_coords(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
