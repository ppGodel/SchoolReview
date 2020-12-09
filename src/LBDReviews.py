from pandas import read_csv, DataFrame
from typing import Callable, List, Tuple
from src.review_helper import format_df_for_upload, evaluate_class, base_create_repo_calif
from src.reviewer.PracticeReviewer import Practice, Course
from src.reviewer.git_retrivers import get_querier_with_credentials
from src.reviewer.scores.LBD_Practice_Scores import lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, \
    lbd_pia
from src.utils.my_pandas_util import save_csv_df

lbd_course = Course("Lab. de Base de datos",
                    [lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8])



def create_lbd_repo_calif(querier: Callable, base_csv_path: str, column_mapping: List[Tuple[str,str]]) -> DataFrame:
    df_lbd = base_create_repo_calif(querier, read_csv(base_csv_path), column_mapping)
    return df_lbd


def format_ldb_review_for_upload(base_df: DataFrame) -> DataFrame:
    return format_df_for_upload(base_df,
                                ["Matricula", "Grupo", "Practica1", "Practica2", "Practica3", "Practica4",
                                 "Practica5", "Practica6", "Practica7", "Practica8", "Total"],
                                "Matricula",
                                lambda x: str(x)[len(str(x))-4:len(str(x))])


def evaluate_lbd_course(practices_list: List[Practice], config_path: str, target_csv_path: str,
                        base_csv_path: str, column_mapping: List[Tuple[str,str]]) -> DataFrame:
    def wrap_create_lbd_class(querier: Callable, csv_path: str,
                              column_mapping: List[Tuple[str, str]]) -> Callable[[str], DataFrame]:
        def create_lbd_course() -> DataFrame:
            return create_lbd_repo_calif(querier, csv_path, column_mapping)
        return create_lbd_course

    querier = get_querier_with_credentials(config_path)
    return evaluate_class(practices_list, wrap_create_lbd_class(querier, base_csv_path, column_mapping),
                          querier, target_csv_path)


if __name__ == '__main__':
    credentials = '../test/resources/my_data.json'
    class_info_csv = "../Classes/LBD_AD_19.csv"
    target_csv = "../Classes/LBD_AD_19_calif.csv"
    upload_csv = "../Classes/LBD_AD_19_upload.csv"
    column_mapping = list(("Matricula","Matricula"),("Nombre","Nombres"),("Apellido Paterno","Primer Apellido"),("Apellido Materno","Segundo Apellido"))
    reviewed_practices = evaluate_lbd_course(lbd_course.practices, credentials, target_csv, class_info_csv, column_mapping)
    save_csv_df(reviewed_practices, target_csv)
    upload_df = format_ldb_review_for_upload(reviewed_practices)
    save_csv_df(upload_df, upload_csv)



