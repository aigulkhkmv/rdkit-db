from dataclasses import dataclass
from time import time
from typing import Union, Tuple

import psycopg2
from loguru import logger
from pony.orm import Database, Required, PrimaryKey, db_session


@dataclass()
class GetQuery:
    mol_smi: str
    search_type: str
    fp_type: Union[bool, str] = False
    sort_by_similarity: bool = False

    @property
    def get_fp_function_name(self) -> str:
        fp_dict = {"mfp2": "morganbv_fp", "ffp2": "featmorganbv_fp", "torsionbv": "torsionbv_fp"}
        try:
            function_name = fp_dict[self.fp_type]
        except KeyError:
            return "FP doesn't exist"
        return function_name

    def __str__(self) -> str:
        if self.search_type == "similarity":
            function_name = self.get_fp_function_name
            if not self.sort_by_similarity:
                return f"select * from public.fps where {self.fp_type}%{function_name}('{self.mol_smi}')"
            else:
                if self.fp_type == "mfp2":
                    return f"select id, tanimoto_sml({self.fp_type}, {function_name}('{self.mol_smi}')) t from public.fps where {self.fp_type}%{function_name}('{self.mol_smi}') order by t DESC"

        if self.search_type == "substructure":
            if not self.sort_by_similarity:
                return f"select * from public.mols where m@>'{self.mol_smi}'"
            else:
                function_name = self.get_fp_function_name
                count_tanimoto = (
                    f"tanimoto_sml({function_name}(m), {function_name}('{self.mol_smi}'))"
                )
                return (
                    f"select id, m, {count_tanimoto} t from public.mols where m@>'{self.mol_smi}' "
                    f"order by t DESC"
                )

        if self.search_type == "equal":
            pass


def pony_db_map(db_name: str, user_name: str) -> Database:
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


class SearchTimeCursor:
    def __init__(self, database_name: str):
        self.database_name = database_name
        conn = psycopg2.connect(database=self.database_name)
        self.curs = conn.cursor()

    def get_time_and_count(
        self,
        mol_smi: str,
        search_type: str,
        fp_type: Union[bool, str] = False,
        sort_by_similarity: bool = False,
        limit: int = 1,
    ) -> Tuple[float, int]:
        logger.info("Postgresql search... ")

        query = str(
            GetQuery(
                mol_smi=mol_smi,
                search_type=search_type,
                fp_type=fp_type,
                sort_by_similarity=sort_by_similarity,
            )
        )
        start_time = time()
        self.curs.execute(query)
        query_res = self.curs.fetchmany(size=limit)
        end_time = time()
        return end_time - start_time, len(query_res)


class SearchPony:
    def __init__(self, database_name: str, user_name: str):
        self.database_name = database_name
        self.user_name = user_name
        self.db = pony_db_map(self.database_name, self.user_name)

    @db_session
    def get_time_and_count(
        self,
        mol_smi: str,
        search_type: str,
        fp_type: Union[bool, str] = False,
        sort_by_similarity: bool = False,
        limit: Union[int, str] = "",
    ) -> Tuple[float, int]:
        logger.info("Pony search..")
        postgresql_query = GetQuery(
            mol_smi=mol_smi,
            search_type=search_type,
            fp_type=fp_type,
            sort_by_similarity=sort_by_similarity,
        )
        logger.info(
            "Query for {} search, fp type {}, sort by similatity {} postgresql: {}",
            search_type,
            fp_type,
            sort_by_similarity,
            postgresql_query,
        )
        start_time = time()
        res = self.db.execute(str(postgresql_query))
        query_res = res.fetchmany(size=limit)
        end_time = time()
        return end_time - start_time, len(query_res)
