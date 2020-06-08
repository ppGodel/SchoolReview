from src.lpe_reviews import evaluate_lpe_course, format_lpe_review_for_upload, lpe_course
from src.LDOOReviews import evaluate_ldoo_course, format_ldoo_review_for_upload
from src.LBDReviews import evaluate_lbd_course, format_ldb_review_for_upload
from src.utils.my_pandas_util import save_csv_df




def review_course(class_info_csv, credentials, target_csv, upload_csv):
    reviewed_practices = evaluate_lpe_course(lpe_course.practices, credentials, target_csv, class_info_csv)
    save_csv_df(reviewed_practices, target_csv)
    upload_df = format_lpe_review_for_upload(reviewed_practices)
    save_csv_df(upload_df, upload_csv)


if __name__ == '__main__':
    import os
    dirname = os.path.dirname(__file__)
    # filename = os.path.join(dirname, 'relative/path/to/file/you/want')
    credentials = os.path.join(dirname, '../../test/resources/my_data.json')

    class_info_csv = os.path.join(dirname, "csv_files/raw_files/lpe_l.csv")
    target_csv = os.path.join(dirname, "csv_files/base_files/lpe_l.csv")
    upload_csv = os.path.join(dirname, "csv_files/base_files/lpe_l_upload.csv")
    #review_course(class_info_csv, credentials, target_csv, upload_csv)


    class_info_csv = os.path.join(dirname, "csv_files/raw_files/lpe_j.csv")
    target_csv = os.path.join(dirname, "csv_files/base_files/lpe_j.csv")
    upload_csv = os.path.join(dirname, "csv_files/base_files/lpe_j_upload.csv")
    review_course(class_info_csv, credentials, target_csv, upload_csv)
