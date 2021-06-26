# rdkit-db
Repo for testing RDkit database

#### Create venv with RDKit and install RDKit cartridge 
```bash
$ conda create -c rdkit -n rdkit-db-env rdkit
$ conda activate 
$ conda install -c conda-forge postgresql
$ conda install -c rdkit rdkit-postgresql
```

```bash
$ work_env/bin/initdb -D path/to/chembl_28
$ work_env/bin/pg_ctl -D path/to/chembl_28 start
$ work_env/bin/createdb chembl_28
# extract db
$ work_env/bin/psql -c 'create extension rdkit' chembl_28
```

Create new database from file with smiles:
```bash
$ work_env/bin/psql -c 'create table raw_data (id SERIAL, smiles text)' chembl_28
$ while read line; do echo $line; done < chembl.txt | work_env/bin/psql -c "copy raw_data (smiles) from stdin" chembl_28
```
Add molecules, gist-index and fingerprints to the database. In postgresql console:
```bash
$ select * into mols from (select id,mol_from_smiles(smiles::cstring) m from raw_data) tmp where m is not null;
$ create index molidx on public.mols using gist(m);
```

Postgresql dump from the ChEMBL website ftp://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest
