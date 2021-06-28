from dataclasses import dataclass
from time import time
from typing import Union

import psycopg2
from pony.orm import Database, Required, PrimaryKey, db_session

from postgresql_db import GetQuery


@dataclass()
class GetQuery:
    mol_smi: str
    search_type: str
    fp_type: Union[bool, str] = False
    sort_by_similarity: bool = False
    limit: Union[int, str] = ""

    @property
    def get_fp_function_name(self) -> str:
        fp_dict = {"mfp2": "morganbv_fp", "ffp2": "featmorganbv_fp", "torsionbv": "torsionbv_fp"}
        try:
            function_name = fp_dict[self.fp_type]
        except KeyError:
            return "FP doesn't exist"
        return function_name

    def __str__(self) -> str:
        limit = ""
        if self.limit:
            limit = f" limit {self.limit}"
        if self.search_type == "similarity":
            function_name = self.get_fp_function_name
            if not self.sort_by_similarity:
                return f"select * from public.fps where {self.fp_type}%{function_name}('{self.mol_smi}'){ limit}"
            else:
                if self.fp_type == "mfp2":
                    return f"select * from get_mfp2_neighbors('{self.mol_smi}'){ limit}"

        if self.search_type == "substructure":
            if not self.sort_by_similarity:
                return f"select * from public.mols where m@>'{self.mol_smi}'{ limit}"
            else:
                function_name = self.get_fp_function_name
                count_tanimoto = (
                    f"tanimoto_sml({function_name}(m), {function_name}('{self.mol_smi}'))"
                )
                return (
                    f"select id, m, {count_tanimoto} t from public.mols where m@>'{self.mol_smi}' "
                    f"order by t DESC{ limit}"
                )

        if self.search_type == "equal":
            pass


class SearchTimePostgres:
    def __init__(self, database_name: str):
        self.database_name = database_name
        conn = psycopg2.connect(database=self.database_name)
        self.curs = conn.cursor()

    def get_fetchone_time(self, query: str) -> float:
        start_time = time()
        self.curs.execute(query)
        self.curs.fetchone()
        end_time = time()
        return end_time - start_time

    def get_fetchall_time(self, query: str) -> float:
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
        limit: Union[int, str] = "",
    ) -> float:
        query = str(
            GetQuery(
                mol_smi=mol_smi,
                search_type=search_type,
                fp_type=fp_type,
                sort_by_similarity=sort_by_similarity,
                limit=limit,
            )
        )
        if first_in:
            return self.get_fetchone_time(query)
        else:
            return self.get_fetchall_time(query)


def pony_db_map(db_name, user_name):
    db = Database()

    class Fps(db.Entity):
        _table_ = "fps"
        id = PrimaryKey(int, auto=True)
        torsionbv = Required(int)
        mfp2 = Required(int)
        ffp2 = Required(int)

    class Mols(db.Entity):
        _table_ = "mols"
        id = PrimaryKey(int, auto=True)
        m = Required(str)

    class Raw_data(db.Entity):
        _table_ = "raw_data"
        id = PrimaryKey(int, auto=True)
        smiles = Required(str)

    class Test_class(db.Entity):
        _table_ = "test_class"
        id = PrimaryKey(int, auto=True)
        test = Required(str)

    db.bind(provider="postgres", user=user_name, host="localhost", database=db_name)
    db.generate_mapping(create_tables=True)
    return db


class SearchTimePony:
    def __init__(self, database_name: str, user_name: str):
        self.database_name = database_name
        self.user_name = user_name
        self.db = pony_db_map(self.database_name, self.user_name)

    @db_session
    def get(self,
            mol_smi: str,
            search_type: str,
            fp_type: Union[bool, str] = False,
            sort_by_similarity: bool = False,
            limit: Union[int, str] = "",
            ):
        postgresql_query = GetQuery(
            mol_smi=mol_smi,
            search_type=search_type,
            fp_type=fp_type,
            sort_by_similarity=sort_by_similarity,
            limit=limit,
        )
        start_time = time()
        res = self.db.execute(str(postgresql_query))
        [i for i in res]
        end_time = time()
        return end_time-start_time
