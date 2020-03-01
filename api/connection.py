"""
Stores connections for nodes, before storing them into the database, 
so the final Brewery objects aren't holding the information themselves, 
because it is going to be handled by the the database
"""
class Connection:

    def __init__(self, brewery_id, length):
        self.brewery_id = brewery_id
        self.length = length