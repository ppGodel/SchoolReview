#!/usr/bin/env python3

from typing import List, Callable, Tuple
from pandas import DataFrame, read_csv

from src.review_helper import format_df_for_upload, evaluate_class, base_create_repo_calif
from src.reviewer.PracticeReviewer import Practice, Course
from src.reviewer.git_retrivers import  get_querier_with_credentials
from src.utils.my_pandas_util import save_csv_df
from src.reviewer.scores.lpc_practice_scorer import lpc_p1, lpc_p2, lpc_p3, lpc_p4, lpc_p5, \
    lpc_p6, lpc_p7, lpc_p8, lpc_p9, lpc_p10, lpc_p11

lpc_course = Course("Laboratorio de Programacion en ciberseguridad",
                    [lpc_p1, lpc_p2, lpc_p3, lpc_p4, lpc_p5, lpc_p6, lpc_p7, lpc_p8, lpc_p9, lpc_p10,
                     lpc_p11])

def create_lpc_repo_calif(querier: Callable, base_csv_path: str, column_mapping: List[Tuple[str,str]]) -> DataFrame:
    df_lbd = base_create_repo_calif(querier, read_csv(base_csv_path), column_mapping)
    return df_lbd


def format_lpc_review_for_upload(base_df: DataFrame) -> DataFrame:
    return format_df_for_upload(base_df,
                                ["Matricula", "Grupo", "Practica1", "Practica2", "Practica3", "Practica4",
                                 "Practica5", "Practica6", "Practica7", "Practica8", "Practica9",
                                 "Practica10", "Pactica11", "Practica12", "Total"],
                                "Matricula",
                                lambda x: str(x)[len(str(x))-4:len(str(x))])


def evaluate_lpc_course(practices_list: List[Practice], config_path: str, target_csv_path: str,
                         base_csv_path: str, column_mapping: List[Tuple[str,str]]) -> DataFrame:
    def wrap_create_lpc_class(querier: Callable, csv_path: str, column_mapping: List[Tuple[str,str]]) -> Callable[[str], DataFrame]:
        def create_lpc_course() -> DataFrame:
            return create_lpc_repo_calif(querier, csv_path, column_mapping)
        return create_lpc_course

    querier = get_querier_with_credentials(config_path)
    return evaluate_class(practices_list, wrap_create_lpc_class(querier, base_csv_path, column_mapping),
                          querier, target_csv_path)
