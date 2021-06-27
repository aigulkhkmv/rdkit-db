from typing import Union

from pony.orm import Database, Required, PrimaryKey, db_session

from db import GetQuery

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


db.bind(provider="postgres", user="aigul", host="localhost", database="chembl_test")
db.generate_mapping(create_tables=True)


@db_session
def get_pony_query(
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
    return db.execute(str(postgresql_query))


res = get_pony_query(
    mol_smi="COc1cc(Nc2nc3cnc(-c4cccnc4)cc3n2C)cc(OC)c1OC", search_type="substructure"
)
print([i for i in res])
