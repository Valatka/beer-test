from bottle import route, run, default_app
import uuid 

from connection import Connection
from brewery import Brewery
from beer_and_coords import BeerAndCoords
from search_results import SearchResults
from graph import Graph


@route('/api/find-path/<latitude>/<longitude>')
def generate_path(latitude, longitude):

    # convert to float
    latitude = float(latitude)
    longitude = float(longitude)

    # generate home id
    unique_id = uuid.uuid4().hex[:12]

    # create graph object
    graph = Graph('beer.db', home_id=unique_id)

    # find path
    result = graph.find_path(latitude, longitude)

    # return result in json
    return result.return_in_json()

if __name__ == '__main__':
	run(host='localhost', port=4000, debug=False)
else:
	app = application = default_app()