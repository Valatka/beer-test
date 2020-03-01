from bottle import route, run

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

run(host='localhost', port=5000, debug=False)