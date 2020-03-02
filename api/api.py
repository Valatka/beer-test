from bottle import route, run, default_app
import uuid 

from connection import Connection
from brewery import Brewery
from beer_and_coords import BeerAndCoords
from search_results import SearchResults
from graph import Graph


@route('/api/find-path/<latitude>/<longitude>/<number_of_runs>')
def generate_path(latitude, longitude, number_of_runs):

    # Validate user input
    try:

        # Check if values are the correct type
        latitude = float(latitude)
        longitude = float(longitude)
        number_of_runs = int(number_of_runs)

        # Check if latitude is in range
        if (latitude < -90 or latitude > 90):
            raise ValueError

        # Check if longitude is in range
        if (longitude < -180 or longitude > 180):
            raise ValueError

        # Check if number_of_runs is range
        if (number_of_runs < 0 or number_of_runs > 20):
            raise ValueError

    except ValueError:
        temp_result = SearchResults()
        temp_result.reset()
        return temp_result.return_in_json()

    # convert to float
    latitude = float(latitude)
    longitude = float(longitude)

    # generate home id
    unique_id = uuid.uuid4().hex[:12]

    # create graph object
    graph = Graph('beer.db', home_id=unique_id, weight=0.504597714410906)

    # find path
    result = graph.genetic_near_neighbour(number_of_runs, latitude, longitude)

    # return result in json
    return result.return_in_json()

if __name__ == '__main__':
	run(host='localhost', port=5000, debug=False)
else:
	app = application = default_app()