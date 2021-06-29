import json
import sys

import pandas as pd
from loguru import logger

sys.path.append("/Users/aigul/Desktop/work/rdkit-db")
from src.postgresql_db import SearchPony, SearchTimeCursor


def get_time_and_count(
    db_name: str, user_name: str, test_mols_path: str, search_type: str, limit: int
):
    logger.info("{} search", search_type)
    if search_type == "pony":
        chembl_db_time = SearchPony(db_name, user_name)
    elif search_type == "postgres":
        chembl_db_time = SearchTimeCursor(db_name)

    with open(test_mols_path, "r") as test_mols:
        test_mols = json.load(test_mols)
    logger.info("Read test mols")

    mols_list = [i for i in test_mols.values()]
    substructure_search, sorted_mfp_substructure = [], []
    similarity_mfp2, sorted_similarity_mfp2 = [], []

    substructure_search_count, sorted_mfp_substructure_count = [], []
    similarity_mfp2_count, sorted_similarity_mfp2_count = [], []

    for mol_smi in mols_list:
        logger.info("Test molecule {}", mol_smi)

        logger.info("Start substructure search for mol {}", mol_smi)
        substructure_time, count_substructure = chembl_db_time.get_time_and_count(
            mol_smi=mol_smi, search_type="substructure", limit=limit
        )
        substructure_search.append(substructure_time)
        substructure_search_count.append(count_substructure)
        logger.info("Time for substructure search {}", substructure_time)

        logger.info("Start sorted substructure search for mol {}", mol_smi)
        (
            sorted_mfp_substructure_time,
            count_sorted_mfp_substructure,
        ) = chembl_db_time.get_time_and_count(
            mol_smi=mol_smi,
            search_type="substructure",
            sort_by_similarity=True,
            fp_type="mfp2",
            limit=limit,
        )
        sorted_mfp_substructure.append(sorted_mfp_substructure_time)
        sorted_mfp_substructure_count.append(count_sorted_mfp_substructure)
        logger.info("Time for sorted substructure search {}", sorted_mfp_substructure_time)

        logger.info("Start similarity search for mol {}", mol_smi)
        similarity_mfp2_time, count_similarity_mfp2 = chembl_db_time.get_time_and_count(
            mol_smi=mol_smi,
            search_type="similarity",
            fp_type="mfp2",
            limit=limit,
        )
        similarity_mfp2.append(similarity_mfp2_time)
        logger.info("!!!!!!!!!!!!!{}", count_similarity_mfp2)
        similarity_mfp2_count.append(count_similarity_mfp2)
        logger.info("Time for similarity search {}", similarity_mfp2_time)

        logger.info("Start sorted similarity search for mol {}", mol_smi)
        sorted_similarity_mfp2_time = chembl_db_time.get(
            mol_smi=mol_smi,
            search_type="similarity",
            fp_type="mfp2",
            sort_by_similarity=True,
        )
        sorted_similarity_mfp2.append(sorted_similarity_mfp2_time)
        logger.info("Time for sorted similarity search {}", sorted_similarity_mfp2_time)

    time_res = {
        "smiles": mols_list,
        f"substructure {limit}": substructure_search,
        f"sorted mfp substructure {limit}": sorted_mfp_substructure,
        f"similarity mfp2 {limit}": similarity_mfp2,
        f"sorted similarity mfp2 {limit}": sorted_similarity_mfp2,
    }

    count_res = {
        "smiles": mols_list,
        f"count substructure {limit}": substructure_search_count,
        f"count sorted mfp substructure {limit}": sorted_mfp_substructure_count,
        f"count similarity mfp2 {limit}": similarity_mfp2_count,
        # TODO add count similarity
    }

    return time_res, count_res


def get_time_with_limits(db_name, user, test_mols, search_type, path_to_save):
    limits = [1, 10, 100, 1000, 20000000]
    res_limits = []
    res_counts = []
    for limit in limits:
        res_lim, res_count = get_time_and_count(db_name, user, test_mols, search_type, limit=limit)
        res_limits.append(res_lim)
        res_counts.append(res_count)

    final_dict = {
        **res_limits[0],
        **res_limits[1],
        **res_limits[2],
        **res_limits[3],
        **res_limits[4],
        **res_counts[0],
        **res_counts[1],
        **res_counts[2],
        **res_counts[3],
        **res_counts[4],
    }
    df = pd.DataFrame(final_dict)
    df.to_excel(path_to_save)


if __name__ == "__main__":
    get_time_with_limits("chembl_test", "aigul", "test_mols.json", "postgres", "test_postgres.xlsx")
