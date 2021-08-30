import json
import sys
from pathlib import Path
from typing import Tuple

import click
import pandas as pd
from loguru import logger

sys.path.append("~rdkit-db")
from src.postgresql_db import SearchPony, SearchTimeCursor


def get_all_time_and_count(
    db_name: str,
    user_name: str,
    test_mols_path: Path,
    search_type: str,
    limit: int,
    port: int,
    password=None,
) -> Tuple[dict, dict]:
    """
    Searches by substructure and similarity for target molecules.
    """
    logger.info("{} search with limit {}", search_type, limit)
    if search_type == "pony":
        chembl_db_time = SearchPony(db_name, user_name, port, password)
    elif search_type == "postgres":
        if password:
            chembl_db_time = SearchTimeCursor(
                port=port, dbname=db_name, user=user_name, password=password
            )
        else:
            chembl_db_time = SearchTimeCursor(port=port, dbname=db_name, user=user_name)

    with test_mols_path.open("r") as test_mols:
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
        similarity_mfp2_count.append(count_similarity_mfp2)
        logger.info("Time for similarity search {}", similarity_mfp2_time)

        logger.info("Start sorted similarity search for mol {}", mol_smi)
        (
            sorted_similarity_mfp2_time,
            count_sorted_similarity_mfp2,
        ) = chembl_db_time.get_time_and_count(
            mol_smi=mol_smi,
            search_type="similarity",
            fp_type="mfp2",
            sort_by_similarity=True,
            limit=limit,
        )
        sorted_similarity_mfp2.append(sorted_similarity_mfp2_time)
        sorted_similarity_mfp2_count.append(count_sorted_similarity_mfp2)
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
        f"count sorted similarity mfp2 {limit}": sorted_similarity_mfp2_count,
    }

    return time_res, count_res


@click.command()
@click.argument("db_name")
@click.argument("user")
@click.argument("port")
@click.argument("test_mols_path", type=Path)
@click.argument("search_type")
@click.argument("path_to_save", type=Path)
@click.argument("password", required=False)
def get_time_with_limits(
    db_name: str,
    user: str,
    port: int,
    test_mols_path: Path,
    search_type: str,
    path_to_save: Path,
    password=None,
) -> None:
    """
    Searches the database for the specified molecules and saves the search time to a excel file.
    """
    limits = [1, 10, 100, 1000, 21000000]
    res_limits = []
    res_counts = []
    for limit in limits:
        res_lim, res_count = get_all_time_and_count(
            db_name, user, test_mols_path, search_type, limit, port, password
        )
        res_limits.append(res_lim)
        res_counts.append(res_count)
    logger.info(res_limits)
    logger.info(res_counts)
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
    df.to_excel(path_to_save.as_posix())


if __name__ == "__main__":
    get_time_with_limits()
