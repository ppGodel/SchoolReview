from typing import Callable

from pandas import DataFrame, read_csv

from src.reviewer.git_retrivers import review_class_by_practice, practice_summary, build_course_from_csv, \
    github_get_repository_list_by
from src.reviewer.scores.LBD_Practice_Scores import lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, \
    lbd_pia


def create_repo_calif(querier: Callable, csv_path: str) -> DataFrame:
    base_columns = ["Matricula", "Nombres", "Apellido Paterno", "Apellido Materno",
                    "Laboratorio a cursar"]
    new_columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido", "Grupo"]
    df_lbd = build_course_from_csv(querier(github_get_repository_list_by),
                                   "Classes/LBD_EJ_19.csv", 'Repositorio',
                                   base_columns, new_columns)
    df_lbd.to_csv(csv_path, sep=',', encoding='utf-8', index=False)
    return df_lbd


practices = [lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, lbd_pia]

class_info_csv = "Classes/LBD_repos_calif.csv"
credentials = 'test/resources/my_data.json'
for practice in practices:
    review_class_by_practice(credentials, practice, class_info_csv, create_repo_calif)
results_df = read_csv(class_info_csv)
results_df["Total"] = sum([results_df[practice.name] for practice in practices])
results_df.to_csv(class_info_csv, sep=',', encoding='utf-8', index=False)
practice_summary(results_df["Total"])
