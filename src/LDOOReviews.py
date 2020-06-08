from typing import List, Callable
from pandas import DataFrame, read_csv

from src.review_helper import format_df_for_upload, evaluate_class, base_create_repo_calif
from src.reviewer.PracticeReviewer import Practice
from src.reviewer.git_retrivers import get_querier_with_credentials
from src.reviewer.scores.LDOOPracticeScores import ldoo_p1, ldoo_p2, ldoo_p3, ldoo_p4, ldoo_p5, \
    ldoo_p6, ldoo_p7, ldoo_p8, ldoo_p9, ldoo_p10
from src.utils.my_pandas_util import save_csv_df


def create_ldoo_repo_calif(querier: Callable, base_csv_path: str) -> DataFrame:
    base_columns = ["Matricula", "Nombres", "Apellido Paterno", "Apellido Materno",
                    "Grupo"]
    new_columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido", "Grupo"]
    df_lbd = base_create_repo_calif(querier, read_csv(base_csv_path), list(zip(new_columns, base_columns)))
    return df_lbd


def format_ldoo_review_for_upload(base_df: DataFrame) -> DataFrame:
    return format_df_for_upload(base_df,
                                ["Matricula", "Grupo", "Practica1", "Practica2", "Practica3", "Practica4",
                                 "Practica5", "Practica6", "Practica7", "Practica8", "Practica9",
                                 "Practica10", "Total"],
                                "Matricula",
                                lambda x: str(x)[len(str(x))-4:len(str(x))])


def evaluate_ldoo_course(practices_list: List[Practice], config_path: str, target_csv_path: str,
                        base_csv_path: str) -> DataFrame:
    def wrap_create_ldoo_class(querier: Callable, csv_path: str) -> Callable[[str], DataFrame]:
        def create_ldoo_course() -> DataFrame:
            return create_ldoo_repo_calif(querier, csv_path)
        return create_ldoo_course

    querier = get_querier_with_credentials(config_path)
    return evaluate_class(practices_list, wrap_create_ldoo_class(querier, base_csv_path),
                          querier, target_csv_path)



if __name__ == '__main__':
    practices = [ldoo_p1, ldoo_p2, ldoo_p3, ldoo_p4, ldoo_p5, ldoo_p6, ldoo_p7, ldoo_p8, ldoo_p9,
                 ldoo_p10]
    class_info_csv = "../Classes/LDOO_AD_19.csv"
    target_csv = "../Classes/LDOO_AD_19_calif.csv"
    credentials = '../test/resources/my_data.json'
    upload_csv = "../Classes/LDOO_AD_19_upload.csv"
    reviewed_practices = evaluate_ldoo_course(practices, credentials, target_csv, class_info_csv)
    save_csv_df(reviewed_practices, target_csv)
    upload_df = format_ldoo_review_for_upload(reviewed_practices)
    save_csv_df(upload_df, upload_csv)
