from time import time

import psycopg2


class DataBase:
    def __init__(self, database_name):
        self.database_name = database_name
        conn = psycopg2.connect(database=self.database_name)
        self.curs = conn.cursor()

    def subs_search_first_in(self, mol_smi):
        self.curs.execute("select * from rdk.mols where m@>%s", (mol_smi,))
        start_time = time()
        self.curs.fetchone()
        end_time = time()
        return end_time - start_time

    def similarity_search(self):
        pass
