import json
import sys

import pandas as pd
from loguru import logger

sys.path.append("/Users/aigul/Desktop/work/rdkit-db")

from src.postgresql_db import SearchTimePostgres, SearchTimePony


def query(db_name, user_name, test_mols_path, xlsx_file_name, search_type):
    logger.info("{} search", search_type)
    if search_type == "pony":
        chembl_db_time = SearchTimePony(db_name, user_name)
    elif search_type == "postgres":
        chembl_db_time = SearchTimePostgres(db_name)

    with open(test_mols_path, "r") as test_mols:
        test_mols = json.load(test_mols)
    logger.info("Read test mols")

    mols_list = [i for i in test_mols.values()]
    substructure_search, sorted_mfp_substructure = [], []
    similarity_mfp2, sorted_similarity_mfp2 = [], []

    for mol_smi in mols_list:
        logger.info("Test molecule {}", mol_smi)

        logger.info("Start substructure search for mol {}", mol_smi)
        substructure_time = chembl_db_time.get(mol_smi=mol_smi, search_type="substructure")
        substructure_search.append(substructure_time)
        logger.info("Time for substructure search {}", substructure_time)

        logger.info("Start sorted substructure search for mol {}", mol_smi)
        sorted_mfp_substructure_time = chembl_db_time.get(mol_smi=mol_smi, search_type="substructure",
                                                          sort_by_similarity=True, fp_type="mfp2")
        sorted_mfp_substructure.append(sorted_mfp_substructure_time)
        logger.info("Time for sorted substructure search {}", sorted_mfp_substructure_time)

        logger.info("Start similarity search for mol {}", mol_smi)
        similarity_mfp2_time = chembl_db_time.get(mol_smi=mol_smi, search_type="similarity", fp_type="mfp2")
        similarity_mfp2.append(similarity_mfp2_time)
        logger.info("Time for similarity search {}", similarity_mfp2_time)

        logger.info("Start sorted similarity search for mol {}", mol_smi)
        sorted_similarity_mfp2_time = chembl_db_time.get(mol_smi=mol_smi, search_type="similarity",
                                                         first_in=False, fp_type="mfp2", sort_by_similarity=True)
        sorted_similarity_mfp2.append(sorted_similarity_mfp2_time)
        logger.info("Time for sorted similarity search {}", sorted_similarity_mfp2_time)

    df = pd.DataFrame(
        {
            "smiles": mols_list,
            "substructure": substructure_search,
            "sorted mfp substructure": sorted_mfp_substructure,
            "similarity mfp2": similarity_mfp2,
            "sorted similarity mfp2": sorted_similarity_mfp2
        }
    )

    logger.info("Save into xlsx file...")
    df.to_excel(xlsx_file_name)


if __name__ == "__main__":
    simple_postgresql("chembl_test", "test_mols.json", "test.xlsx")
