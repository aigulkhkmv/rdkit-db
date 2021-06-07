# rdkit-db
Repo for testing RDkit database

#### Create venv with RDKit and install RDKit cartridge 
```bash
$ conda create -c rdkit -n rdkit-db-env rdkit
$ conda activate 
$ conda install -c conda-forge postgresql
$ conda install -c rdkit rdkit-postgresql
```

#### init database:
```bash
$ initdb -D ~/postgresdata
$ /path/to/postgres -D ~/postgresdata
```

Start by downloading and installing the postgresql dump from the ChEMBL website ftp://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest


 