from datetime import datetime
from typing import Callable, List, Tuple

from pandas import DataFrame
from src.utils.my_pandas_util import parse_csv_df
from src.reviewer.git_retrivers import build_course_from_csv, review_class_by_practice, practice_summary, \
    get_create_review_df
from src.reviewer.github_request_client import github_get_repository_list_by


def base_create_repo_calif(querier: Callable, students_df: DataFrame, column_names_map: List[Tuple[str, str]]) -> DataFrame:
    return build_course_from_csv(querier(github_get_repository_list_by), students_df,
                                 'Repositorio',
                                 column_names_map)


def format_df_for_upload(base_df: DataFrame, selected_columns: List[str], key_column: str, key_value_xform: Callable[[str], str]) -> DataFrame:
    new_df = base_df.reindex(selected_columns, axis='columns')
    new_df[key_column] = new_df[key_column].map(key_value_xform)
    return new_df


def evaluate_class(practices_list: List, create_repo_calif: Callable[[str], DataFrame], querier: Callable,
                   target_csv_path: str) -> DataFrame:
    course_practices_df = get_create_review_df(create_repo_calif, target_csv_path)
    for practice in practices_list:
        review_practice(course_practices_df, practice, querier)
    course_practices_df["Total"] = sum([course_practices_df[practice.name] for practice in practices_list])
    practice_summary(course_practices_df["Total"])
    return course_practices_df


def review_practice(course_practices_df, practice, querier):
    print("Reviewing: {} at {}".format(practice.name, datetime.now()))
    practice_calif = review_class_by_practice(querier, practice, course_practices_df)
    print("Finish {} at {}".format(practice.name, datetime.now()))
    practice_summary(practice_calif)
    course_practices_df[practice.name] = practice_calif