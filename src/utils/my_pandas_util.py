from pandas import DataFrame, read_csv


def parse_csv_df(csv_path: str) -> DataFrame:
    students_df = read_csv(csv_path)
    return students_df


def save_csv_df(df: DataFrame, target_path) -> None:
    df.to_csv(target_path, sep=',', encoding='utf-8', index=False)
