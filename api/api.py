from bottle import route, run, default_app

from connection import Connection
from brewery import Brewery
from beer_and_coords import BeerAndCoords
from search_results import SearchResults
from graph import Graph


@route('/api/find-path/<latitude>/<longitude>')
def generate_path(latitude, longitude):

    latitude = float(latitude)
    longitude = float(longitude)

    graph = Graph('beer.db')

    result = graph.find_path(latitude, longitude)

    return result.return_in_json()

if __name__ == '__main__':
	run(host='localhost', port=4000, debug=False)
else:
	app = application = default_app()