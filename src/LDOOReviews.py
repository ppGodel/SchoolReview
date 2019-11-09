from typing import  List
from pandas import DataFrame, read_csv
from src.reviewer.git_retrivers import practice_summary, build_course_from_csv, \
    review_class_by_practice
from src.reviewer.github_request_client import github_get_repository_list_by
from src.reviewer.scores.LDOOPracticeScores import *


def create_repo_calif(querier: Callable, base_csv_path: str, target_csv_path: str) -> DataFrame:
    base_columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido",
                    "Grupo"]
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


practices = [ldoo_p1, ldoo_p2, ldoo_p3, ldoo_p4, ldoo_p5, ldoo_p6, ldoo_p7, ldoo_p8, ldoo_p9,
             ldoo_p10]

class_info_csv = "../Classes/LDOO_AD_19.csv"
target_csv = "../Classes/LDOO_AD_19_calif.csv"
credentials = '../test/resources/my_data.json'

evaluate_class(practices, credentials, target_csv, class_info_csv)
