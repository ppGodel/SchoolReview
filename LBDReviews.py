import datetime
import json
from typing import Callable

from pandas import DataFrame, read_csv, Series

from PracticeReviewer import parse_csv_df, review_practice_from_df, Practice, \
    lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, lbd_pia
from Students import get_querier, github_get_file_info, github_get_commit_list_of_a_file, \
    build_course_from_csv, github_get_repository_list_by


def get_querier_with_credentials():
    with open('test/resources/my_data.json') as f:
        my_data = json.load(f)
    return get_querier(my_data["client_id"], my_data["client_secret"])

def review_ldb_by_practice(practice: Practice, csv_path):
    querier = get_querier_with_credentials()
    try:
        df_lbd = parse_csv_df(csv_path)
    except FileNotFoundError:
        df_lbd = create_repo_calif(querier, csv_path)
    practice_calif = review_practice_from_df(df_lbd, querier(github_get_file_info),
                                             querier(github_get_commit_list_of_a_file),
                                             practice)
    df_lbd[practice.name] = practice_calif
    df_lbd.to_csv(csv_path, sep=',', encoding='utf-8', index=False)
    practice_summary(practice_calif)


def create_repo_calif(querier: Callable, csv_path: str) -> DataFrame:
    base_columns = ["Matricula", "Nombres", "Apellido Paterno", "Apellido Materno",
                    "Laboratorio a cursar"]
    new_columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido", "Grupo"]
    df_lbd = build_course_from_csv(querier(github_get_repository_list_by),
                                   "Classes/LBD_EJ_19.csv", 'Repositorio',
                                   base_columns, new_columns)
    df_lbd.to_csv(csv_path, sep=',', encoding='utf-8', index=False)
    return df_lbd


def practice_summary(practice_calif: Series):
    print("Media: {}, \n Dist: \n{}".format(practice_calif.mean(), practice_calif.groupby(practice_calif).agg('count')))


practices = [lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, lbd_pia]

class_info_csv = "Classes/LBD_repos_calif.csv"
for practice in practices:
    print("Reviewing: {} at {}".format(practice.name, datetime.datetime.now()))
    review_ldb_by_practice(practice, class_info_csv)
print("Finish at {}".format(datetime.datetime.now()))
results_df = read_csv(class_info_csv)
results_df["Total"] = sum([results_df[practice.name] for practice in practices])
results_df.to_csv(class_info_csv, sep=',', encoding='utf-8', index=False)
practice_summary(results_df["Total"])

