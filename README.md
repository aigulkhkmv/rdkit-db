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
$ work_env/bin/initdb -D path/to/data
$ work_env/bin/pg_ctl -D path/to/data -l logfile start
# change postgresql configuration (postgresql.conf)
# synchronous_commit = off # immediate fsync at commit
# full_page_writes = off # recover from partial page writes
# shared_buffers = 2048MB # min 128kB
$ work_env/bin/createdb db_name
# extract db
$ work_env/bin/psql -c 'create extension rdkit' db_name
```

Create new database from file with smiles:
```bash
$ work_env/bin/psql -c 'create table raw_data (id SERIAL, smiles text)' db_name
$ while read line; do echo $line; done < data.txt | work_env/bin/psql -c "copy raw_data (smiles) from stdin" db_name
```
Add molecules, gist-index and fingerprints to the database. In postgresql console:
```bash
$ select * into mols from (select id,mol_from_smiles(smiles::cstring) m from raw_data) tmp where m is not null;
$ create index molidx on public.mols using gist(m);
$ alter table mols  add primary key (id);
$ select id,morganbv_fp(m) as mfp2 into public.fps from mols;
$ create index fps_mfp2_idx on public.fps using gist(mfp2);
$ alter table public.fps add primary key (id);
```

Run script with time check:
```bash
$ python3 check_time.py db_name user_name port path_to_outpu.json search_type path_save_results.xlsx password
```
search_type: postgres/pony
password is the database password, this is an optional element
