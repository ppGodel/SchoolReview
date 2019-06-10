from typing import Callable, List

from pandas import DataFrame, read_csv, Series

from PracticeReviewer import practice_summary, review_class_by_practice
from LBD_Practice_Scores import lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, \
    lbd_pia
from Students import build_course_from_csv, github_get_repository_list_by


def create_repo_calif(querier: Callable, csv_path: str) -> DataFrame:
    base_columns = ["Matricula", "Nombres", "Apellido Paterno", "Apellido Materno",
                    "Laboratorio a cursar"]
    new_columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido", "Grupo"]
    df_lbd = build_course_from_csv(querier(github_get_repository_list_by),
                                   "Classes/LBD_EJ_19.csv", 'Repositorio',
                                   base_columns, new_columns)
    df_lbd.to_csv(csv_path, sep=',', encoding='utf-8', index=False)
    return df_lbd


def evaluate_class(practices_list: List, config_path: str, csv_path):
    # for practice in practices_list:
    #     review_class_by_practice(config_path, practice, csv_path, create_repo_calif)
    results_df = read_csv(csv_path)
    results_df["Total"] = sum([results_df[practice.name] for practice in practices_list])
    results_df.to_csv(csv_path, sep=',', encoding='utf-8', index=False)
    practice_summary(results_df["Total"])


practices = [lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, lbd_pia]
class_info_csv = "Classes/LBD_repos_calif_segundas.csv"
credentials = 'test/resources/my_data.json'

evaluate_class(practices, credentials, class_info_csv)


