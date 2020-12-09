import sys
sys.path.append('../../')

from src.lpc_reviewer import evaluate_lpc_course, format_lpc_review_for_upload, lpc_course
from src.LDOOReviews import evaluate_ldoo_course, format_ldoo_review_for_upload
from src.LBDReviews import evaluate_lbd_course, format_ldb_review_for_upload, lbd_course
from src.reviewer.PracticeReviewer import Practice, Course
from src.utils.my_pandas_util import save_csv_df
from typing import Callable, List, Tuple
from pandas import DataFrame


def review_course(class_info_csv: str, credentials: str, target_csv: str,
                  base_columns: List[Tuple[str,str]], upload_csv: str, evaluator:
                  Callable[[List[Practice], str, str, str, List[Tuple[str,str]]], DataFrame],
                  course: Course):
    reviewed_practices = evaluator(course.practices,
                                   credentials,
                                   target_csv,
                                   class_info_csv,
                                   base_columns)
    save_csv_df(reviewed_practices, target_csv)
    upload_df = format_lpc_review_for_upload(reviewed_practices)
    save_csv_df(upload_df, upload_csv)


if __name__ == '__main__':
    import os
    dirname = os.path.dirname(__file__)
    print(dirname)
    # filename = os.path.join(dirname, 'relative/path/to/file/you/want')
    credentials = os.path.join(dirname, '../../test/resources/my_data.json')

    # class_info_csv = os.path.join(dirname, "csv_files/raw_files/LBD.csv")
    # base_columns= [("Email", "Email"), ("Nombre", "Name"), ("Matricula","Matricula"), ("Clase","Clase")]
    # target_csv = os.path.join(dirname, "csv_files/base_files/lbd_j.csv")
    # upload_csv = os.path.join(dirname, "csv_files/base_files/lbd_j_upload.csv")
    # review_course(class_info_csv, credentials, target_csv, base_columns, upload_csv,
    #               evaluate_lbd_course, lbd_course)


    # class_info_csv = os.path.join(dirname, "csv_files/raw_files/LPC_S_8.csv")
    # base_columns= [("Email", "Email"), ("Nombre", "Name"), ("Matricula","Matricula"), ("Clase","Clase")]
    # target_csv = os.path.join(dirname, "csv_files/base_files/lpc_s_8.csv")
    # upload_csv = os.path.join(dirname, "csv_files/base_files/lpc_s_8_upload.csv")
    # review_course(class_info_csv, credentials, target_csv, base_columns, upload_csv,
    #               evaluate_lpc_course, lpc_course)
    # class_info_csv = os.path.join(dirname, "csv_files/raw_files/LPC_S_10.csv")
    # base_columns= [("Email", "Email"), ("Nombre", "Name"), ("Matricula","Matricula"), ("Clase","Clase")]
    # target_csv = os.path.join(dirname, "csv_files/base_files/lpc_s_10.csv")
    # upload_csv = os.path.join(dirname, "csv_files/base_files/lpc_s_10_upload.csv")
    # review_course(class_info_csv, credentials, target_csv, base_columns, upload_csv,
    #               evaluate_lpc_course, lpc_course)
    class_info_csv = os.path.join(dirname, "csv_files/raw_files/LPC_S_12.csv")
    base_columns= [("Email", "Email"), ("Nombre", "Name"), ("Matricula","Matricula"), ("Clase","Clase")]
    target_csv = os.path.join(dirname, "csv_files/base_files/lpc_s_12.csv")
    upload_csv = os.path.join(dirname, "csv_files/base_files/lpc_s_12_upload.csv")
    review_course(class_info_csv, credentials, target_csv, base_columns, upload_csv,
                  evaluate_lpc_course, lpc_course)
