from pony.orm import Database, Required, show, PrimaryKey

db = Database()


class Fps(db.Entity):
    id = PrimaryKey(int, auto=True)
    torsionbv = Required(int)
    mfp2 = Required(int)
    ffp2 = Required(int)


class Mols(db.Entity):
    id = PrimaryKey(int, auto=True)
    m = Required(str)


class Raw_data(db.Entity):
    id = PrimaryKey(int, auto=True)
    smiles = Required(str)


db.bind(provider='postgres', user='aigul', host='localhost', database='chembl_test')
db.generate_mapping(create_tables=True)

show(Mols)
