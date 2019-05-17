from typing import Callable

from pandas import DataFrame, read_csv

from LDOOPracticeScores import ldoo_p1
from PracticeReviewer import review_class_by_practice, practice_summary
from Students import build_course_from_csv, github_get_repository_list_by


def create_repo_calif(querier: Callable, csv_path: str) -> DataFrame:
    base_columns = ["Matricula", "Nombres", "Apellido Paterno", "Apellido Materno",
                    "Laboratorio a cursar"]
    new_columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido", "Grupo"]
    df_lbd = build_course_from_csv(querier(github_get_repository_list_by),
                                   "Classes/LDOO_EJ_19.csv", 'Repositorio',
                                   base_columns, new_columns)
    df_lbd.to_csv(csv_path, sep=',', encoding='utf-8', index=False)
    return df_lbd


practices = [ldoo_p1]

class_info_csv = "Classes/LDOO_repos_calif.csv"
credentials = 'test/resources/my_data.json'
for practice in practices:
    review_class_by_practice(credentials, practice, class_info_csv, create_repo_calif)
results_df = read_csv(class_info_csv)
results_df["Total"] = sum([results_df[practice.name] for practice in practices])
results_df.to_csv(class_info_csv, sep=',', encoding='utf-8', index=False)
practice_summary(results_df["Total"])
