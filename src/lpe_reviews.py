from typing import List, Callable
from pandas import DataFrame, read_csv

from src.review_helper import format_df_for_upload, evaluate_class, base_create_repo_calif
from src.reviewer.PracticeReviewer import Practice, Course
from src.reviewer.git_retrivers import  get_querier_with_credentials
from src.reviewer.scores.lpe_practice_scorer import lpe_p1, lpe_p2, lpe_p3, lpe_p4, lpe_p5, \
    lpe_p6, lpe_p7, lpe_p8, lpe_p9, lpe_p10, lpe_p11, lpe_p12, lpe_p13, lpe_p14
from src.utils.my_pandas_util import save_csv_df


lpe_course = Course("Lab. Programación Estructurada",
                    [lpe_p1, lpe_p2, lpe_p3, lpe_p4, lpe_p5, lpe_p6, lpe_p7, lpe_p8, lpe_p9, lpe_p10,
                     lpe_p11, lpe_p12, lpe_p13, lpe_p14])

def create_lpe_repo_calif(querier: Callable, base_csv_path: str) -> DataFrame:
    base_columns = ["Matricula", "Nombres", "Primer Apellido", "Segundo Apellido"]
    new_columns = ["Matricula", "Nombres", "Primer apellido", "Segundo apellido"]
    df_lbd = base_create_repo_calif(querier, read_csv(base_csv_path), list(zip(new_columns, base_columns)))
    return df_lbd


def format_lpe_review_for_upload(base_df: DataFrame) -> DataFrame:
    return format_df_for_upload(base_df,
                                ["Matricula", "Grupo", "Practica1", "Practica2", "Practica3", "Practica4",
                                 "Practica5", "Practica6", "Practica7", "Practica8", "Practica9",
                                 "Practica10", "Total"],
                                "Matricula",
                                lambda x: str(x)[len(str(x))-4:len(str(x))])


def evaluate_lpe_course(practices_list: List[Practice], config_path: str, target_csv_path: str,
                         base_csv_path: str) -> DataFrame:
    def wrap_create_lpe_class(querier: Callable, csv_path: str) -> Callable[[str], DataFrame]:
        def create_lpe_course() -> DataFrame:
            return create_lpe_repo_calif(querier, csv_path)
        return create_lpe_course

    querier = get_querier_with_credentials(config_path)
    return evaluate_class(practices_list, wrap_create_lpe_class(querier, base_csv_path),
                          querier, target_csv_path)


if __name__ == '__main__':
    class_info_csv = "../Classes/LDOO_AD_19.csv"
    target_csv = "../Classes/LDOO_AD_19_calif.csv"
    credentials = '../test/resources/my_data.json'
    upload_csv = "../Classes/LDOO_AD_19_upload.csv"
    reviewed_practices = evaluate_lpe_course(lpe_course.practices, credentials, target_csv, class_info_csv)
    save_csv_df(reviewed_practices, target_csv)
    upload_df = format_lpe_review_for_upload(reviewed_practices)
    save_csv_df(upload_df, upload_csv)
