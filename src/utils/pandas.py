from pandas import DataFrame, read_csv


def parse_csv_df(csv_path: str) -> DataFrame:
    students_df = read_csv(csv_path)
    return students_df