from dataclasses import dataclass
from time import time
from typing import Union

import psycopg2


@dataclass()
class GetQuery:
    mol_smi: str
    search_type: str
    fp_type: Union[bool, str] = False

    def __str__(self):
        if self.search_type == "similarity":
            if self.fp_type == "mfp2":
                return f"select * from rdk.fps where mfp2%morganbv_fp('{self.mol_smi}')"
            if self.fp_type == "ffp2":
                return f"select * from rdk.fps where ffp2%featmorganbv_fp('{self.mol_smi}')"
            if self.fp_type == "torsionbv":
                return f"select * from rdk.fps where torsionbv%torsionbv_fp('{self.mol_smi}')"
        if self.search_type == "substructure":
            return f"select * from rdk.mols where m@>'{self.mol_smi}'"
        if self.search_type == "equal":
            pass


class SearchTime:
    def __init__(self, database_name: str):
        self.database_name = database_name
        conn = psycopg2.connect(database=self.database_name)
        self.curs = conn.cursor()

    def get_fetchone_time(self):
        start_time = time()
        self.curs.fetchone()
        end_time = time()
        return end_time - start_time

    def get(
        self,
        mol_smi: str,
        search_type: str,
        first_in: bool = True,
        fp_type: Union[bool, str] = False,
    ):
        query = str(GetQuery(mol_smi=mol_smi, search_type=search_type, fp_type=fp_type))
        self.curs.execute(query)
        if first_in:
            return self.get_fetchone_time()
