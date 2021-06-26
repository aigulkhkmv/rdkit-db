from pony.orm import Database, Required, show

db = Database()


class Mols(db.Entity):
    m = Required(str)


class Features(db.Entity):
    torsion_fp = Required()


db.bind(provider='postgres', user='aigul', host='localhost', database='chembl_smi')
db.generate_mapping(create_tables=True)

show(Mols)
