from beer_and_coords import BeerAndCoords

# Brewery class used to store brewery specific information extends BeerAndCoords
class Brewery(BeerAndCoords):

    def __init__(self, name="", brewery_id="", beer=[], latitude="", longitude=""):
        super().__init__(beer, latitude, longitude)
        self.name = name
        self.brewery_id = brewery_id
