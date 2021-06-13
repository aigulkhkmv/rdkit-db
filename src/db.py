from time import time

import psycopg2


class SearchTime:
    def __init__(self, database_name: str):
        self.database_name = database_name
        conn = psycopg2.connect(database=self.database_name)
        self.curs = conn.cursor()

    def subs_search_first_in(self, mol_smi: str):
        self.curs.execute("select * from rdk.mols where m@>%s", (mol_smi,))
        start_time = time()
        self.curs.fetchone()
        end_time = time()
        return end_time - start_time

    def similarity_search(self, fp_type: str, mol_smi: str):
        #TODO add morganbv_fp function usage
        if fp_type == "mfp2":
            # self.curs.callproc("morganbv_fp", (mol_smi,))
            # fp_for_mol = self.curs.fetchone()[0]
            # print(fp_for_mol)
            fp_for_mol = self.curs.execute("CALL morganbv_fp(%s);", (mol_smi,))
            # fp_for_mol = self.curs.execute("SELECT morganbv_fp(%s)", (mol_smi,))
            self.curs.execute("select * from rdk.fps where mfp2%s", fp_for_mol)
            start_time = time()
            self.curs.fetchone()
            end_time = time()
            return end_time - start_time
