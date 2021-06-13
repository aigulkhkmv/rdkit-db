import psycopg2
from time import time


class DataBase:
    def __init__(self, database_name):
        self.database_name = database_name
        conn = psycopg2.connect(database=self.database_name)
        curs = conn.cursor()
        self.curs = curs

    def subs_search_first_in(self):
        self.curs.execute("select * from rdk.mols where m@>%s", ("c1ccccc1O",))
        start_time = time()
        self.curs.fetcone()
        end_time = time()
        return end_time - start_time
