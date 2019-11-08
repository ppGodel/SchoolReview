import datetime
from typing import Callable, List

from pandas import DataFrame, read_csv

from src.reviewer.git_retrivers import review_class_by_practice, practice_summary, build_course_from_csv
from src.reviewer.github_request_client import github_get_repository_list_by
from src.reviewer.scores.LBD_Practice_Scores import lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, \
    lbd_pia


def create_repo_calif(querier: Callable, base_csv_path: str, target_csv_path: str) -> DataFrame:
    base_columns = ["Matricula", "Nombres", "Apellido Paterno", "Apellido Materno",
                    "Laboratorio a cursar"]
    new_columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido", "Grupo"]
    df_lbd = build_course_from_csv(querier(github_get_repository_list_by),
                                   base_csv_path, 'Repositorio',
                                   base_columns, new_columns)
    df_lbd.to_csv(target_csv_path, sep=',', encoding='utf-8', index=False)
    return df_lbd


def evaluate_class(practices_list: List, config_path: str, target_csv_path: str,
                   base_csv_path: str):
    for practice in practices_list:
        print("Reviewing: {} at {}".format(practice.name, datetime.now()))
        review_class_by_practice(config_path, practice, target_csv_path, base_csv_path,
                                 create_repo_calif)
        print("Finish {} at {}".format(practice.name, datetime.now()))
    results_df = read_csv(target_csv_path)
    results_df["Total"] = sum([results_df[practice.name] for practice in practices_list])
    results_df.to_csv(target_csv_path, sep=',', encoding='utf-8', index=False)
    practice_summary(results_df["Total"])


practices = [lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, lbd_pia]
class_info_csv = "Classes/LBD_AD_19.csv"
target_csv = "../Classes/LBD_AD_19_calif.csv"
credentials = 'test/resources/my_data.json'

evaluate_class(practices, credentials, target_csv, class_info_csv)


