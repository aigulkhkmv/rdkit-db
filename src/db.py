from dataclasses import dataclass
from time import time
from typing import Union

import psycopg2


@dataclass()
class GetQuery:
    mol_smi: str
    search_type: str
    fp_type: Union[bool, str] = False
    sort_by_similarity: bool = False

    def get_function_name(self):
        fp_dict = {"mfp2": "morganbv_fp", "ffp2": "featmorganbv_fp", "fps": "torsionbv_fp"}
        try:
            function_name = fp_dict[self.fp_type]
        except KeyError:
            return "FP doesn't exist"
        return function_name

    def __str__(self):
        if self.search_type == "similarity":
            function_name = self.get_function_name()
            if not self.sort_by_similarity:
                return (
                    f"select * from rdk.fps where {self.fp_type}%{function_name}('{self.mol_smi}')"
                )
            else:
                if self.fp_type == "mfp2":
                    return f"select * from get_mfp2_neighbors('{self.mol_smi}')"

        if self.search_type == "substructure":
            if not self.sort_by_similarity:
                return f"select * from rdk.mols where m@>'{self.mol_smi}'"
            else:
                function_name = self.get_function_name()
                count_tanimoto = (
                    f"tanimoto_sml({function_name}(m), {function_name}('{self.mol_smi}'))"
                )
                return f"select molregno, m, {count_tanimoto} as tanimoto from rdk.mols where m@>'{self.mol_smi}' order by {count_tanimoto} DESC"

        if self.search_type == "equal":
            pass


class SearchTime:
    def __init__(self, database_name: str):
        self.database_name = database_name
        conn = psycopg2.connect(database=self.database_name)
        self.curs = conn.cursor()

    def get_fetchone_time(self, query):
        start_time = time()
        self.curs.execute(query)
        print(self.curs.fetchone())
        end_time = time()
        return end_time - start_time

    def get_fetchall_time(self, query):
        start_time = time()
        self.curs.execute(query)
        self.curs.fetchall()
        end_time = time()
        return end_time - start_time

    def get(
        self,
        mol_smi: str,
        search_type: str,
        first_in: bool = True,
        fp_type: Union[bool, str] = False,
        sort_by_similarity: bool = False,
    ):
        query = str(
            GetQuery(
                mol_smi=mol_smi,
                search_type=search_type,
                fp_type=fp_type,
                sort_by_similarity=sort_by_similarity,
            )
        )
        if first_in:
            return self.get_fetchone_time(query)
        else:
            return self.get_fetchall_time(query)
