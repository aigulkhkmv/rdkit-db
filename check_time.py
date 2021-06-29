import json
import sys
from typing import Union

import pandas as pd
from loguru import logger

sys.path.append("/Users/aigul/Desktop/work/rdkit-db")
from src.postgresql_db import SearchTimePostgres, SearchTimePony, SearchTimeCursor


def get_time(db_name, user_name, test_mols_path, search_type, limit: Union[int, str] = ""):
    logger.info("{} search", search_type)
    if search_type == "pony":
        chembl_db_time = SearchTimePony(db_name, user_name)
    elif search_type == "postgres":
        chembl_db_time = SearchTimePostgres(db_name)
    elif search_type == "cursor":
        chembl_db_time = SearchTimeCursor(db_name)

    with open(test_mols_path, "r") as test_mols:
        test_mols = json.load(test_mols)
    logger.info("Read test mols")

    mols_list = [i for i in test_mols.values()]
    substructure_search, sorted_mfp_substructure = [], []
    similarity_mfp2, sorted_similarity_mfp2 = [], []

    for mol_smi in mols_list:
        logger.info("Test molecule {}", mol_smi)

        logger.info("Start substructure search for mol {}", mol_smi)
        substructure_time = chembl_db_time.get(
            mol_smi=mol_smi, search_type="substructure", limit=limit
        )
        substructure_search.append(substructure_time)
        logger.info("Time for substructure search {}", substructure_time)

        logger.info("Start sorted substructure search for mol {}", mol_smi)
        sorted_mfp_substructure_time = chembl_db_time.get(
            mol_smi=mol_smi,
            search_type="substructure",
            sort_by_similarity=True,
            fp_type="mfp2",
            limit=limit,
        )
        sorted_mfp_substructure.append(sorted_mfp_substructure_time)
        logger.info("Time for sorted substructure search {}", sorted_mfp_substructure_time)

        logger.info("Start similarity search for mol {}", mol_smi)
        similarity_mfp2_time = chembl_db_time.get(
            mol_smi=mol_smi,
            search_type="similarity",
            fp_type="mfp2",
            limit=limit,
        )
        similarity_mfp2.append(similarity_mfp2_time)
        logger.info("Time for similarity search {}", similarity_mfp2_time)

        # logger.info("Start sorted similarity search for mol {}", mol_smi)
        # sorted_similarity_mfp2_time = chembl_db_time.get(
        #     mol_smi=mol_smi,
        #     search_type="similarity",
        #     first_in=False,
        #     fp_type="mfp2",
        #     sort_by_similarity=True,
        # )
        # sorted_similarity_mfp2.append(sorted_similarity_mfp2_time)
        # logger.info("Time for sorted similarity search {}", sorted_similarity_mfp2_time)

    time_res = {
        "smiles": mols_list,
        f"substructure {limit}": substructure_search,
        f"sorted mfp substructure {limit}": sorted_mfp_substructure,
        f"similarity mfp2 {limit}": similarity_mfp2,
    }
    # "sorted similarity mfp2": sorted_similarity_mfp2
    # }

    return time_res


def get_time_with_limits(path_to_save):
    limits = [1, 10, 100, 1000, 20000000]
    res_limits = []
    for limit in limits:
        res_limits.append(get_time("chembl_test", "aigul", "test_mols.json", "pony", limit=limit))
        # res_limits.append(get_time("chembl_test", "aigul", "test_mols.json", "cursor", limit=limit))
    final_dict = {
        **res_limits[0],
        **res_limits[1],
        **res_limits[2],
        **res_limits[3],
        **res_limits[4],
    }
    df = pd.DataFrame(final_dict)
    df.to_excel(path_to_save)


if __name__ == "__main__":
    get_time_with_limits("test.xlsx")
