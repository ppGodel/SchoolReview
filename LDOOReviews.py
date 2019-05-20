from typing import Callable

from pandas import DataFrame, read_csv

from LDOOPracticeScores import *
from PracticeReviewer import review_class_by_practice, practice_summary
from Students import build_course_from_csv, github_get_repository_list_by


def create_repo_calif(querier: Callable, csv_path: str) -> DataFrame:
    base_columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido",
                    "Grupo"]
    new_columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido", "Grupo"]
    df_lbd = build_course_from_csv(querier(github_get_repository_list_by),
                                   "Classes/LDOO_EJ_19.csv", 'Repositorio',
                                   base_columns, new_columns)
    df_lbd.to_csv(csv_path, sep=',', encoding='utf-8', index=False)
    return df_lbd


practices = [ldoo_p1, ldoo_p2, ldoo_p3, ldoo_p4, ldoo_p5, ldoo_p6, ldoo_p7, ldoo_p8, ldoo_p9, ldoo_p10]

class_info_csv = "Classes/LDOO_repos_calif.csv"
credentials = 'test/resources/my_data.json'
for practice in practices:
    review_class_by_practice(credentials, practice, class_info_csv, create_repo_calif)
results_df = read_csv(class_info_csv)
results_df["Total"] = sum([results_df[practice.name] for practice in practices])
results_df.to_csv(class_info_csv, sep=',', encoding='utf-8', index=False)
practice_summary(results_df["Total"])
