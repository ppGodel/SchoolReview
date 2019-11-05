import datetime
from functools import partial
from typing import Callable, Dict, List, Tuple

import rx
from pandas import DataFrame, Series
from rx import operators as op

from src.Students import github_get_file_info, github_get_commit_list_of_a_file
from src.reviewer.PracticeReviewer import Practice, review_practice_from_df, \
    score_function_type, PracticeFile, get_practice_files, _check_and_review_practice, get_querier_with_credentials
from src.utils import reactive
from src.utils.pandas import parse_csv_df


def review_practice_from_df_from_git(df: DataFrame, fn_get_file_info: Callable[[str], Dict],
                                     fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                                     practice: Practice) -> Series:
    check_and_review_practice_from_row = check_and_review_practice_from_git(
        fn_get_file_info, fn_get_commit_list_of_a_file, practice)
    return review_practice_from_df(df, check_and_review_practice_from_row)


def get_practice_file_from_git(fn_get_file_info: Callable[[str], Dict],
                               fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                               practice: Practice) -> List[Tuple[score_function_type,
                                                                 str, PracticeFile]]:
    return [(practice.score_function, practice.name, practice_file_info) for practice_file_info in
            get_practice_files(fn_get_file_info, fn_get_commit_list_of_a_file,
                               practice.aliases, practice.as_dir) if practice_file_info]


def check_and_review_practice_from_git(fn_get_file_info: Callable[[str, str, str], Dict],
                                       fn_get_commit_list_of_a_file: Callable[[str, str, str, str], List[Dict]],
                                       practice: Practice) -> Callable[[Series], int]:
    def _check_and_review_practice_from_git(row: Series) -> int:
        get_file = partial(fn_get_file_info, row.get("repo_site"), row.get("repo_user"), row.get("repo_name"))
        get_commit_list = partial(fn_get_commit_list_of_a_file, row.get("repo_site"), row.get("repo_user"),
                                  row.get("repo_name"))
        get_practice_list = partial(get_practice_file_from_git, get_file, get_commit_list)
        return _check_and_review_practice(get_practice_list, row, practice)

    return _check_and_review_practice_from_git


def review_class_by_practice(config_path: str, practice_info: Practice, csv_path: str,
                             create_repo_calif_df: Callable[[Callable, str], DataFrame]):
    print("Reviewing: {} at {}".format(practice_info.name, datetime.now()))
    querier = get_querier_with_credentials(config_path)
    try:
        df_lbd = parse_csv_df(csv_path)
    except FileNotFoundError:
        df_lbd = create_repo_calif_df(querier, csv_path)
    practice_calif = review_practice_from_df_from_git(df_lbd, querier(github_get_file_info),
                                                      querier(github_get_commit_list_of_a_file),
                                                      practice_info)
    df_lbd[practice_info.name] = practice_calif
    df_lbd.to_csv(csv_path, sep=',', encoding='utf-8', index=False)
    practice_summary(practice_calif)
    print("Finish at {}".format(datetime.now()))


def rx_review_practice_from_df(df: DataFrame, fn_get_file_info: Callable[[str, str, str], Dict],
                               fn_get_commit_list_of_a_file: Callable[[str, str, str, str], List[Dict]],
                               practice: Practice) -> rx.Observable[Series]:
    practice_reviewer = check_and_review_practice_from_git(fn_get_file_info, fn_get_commit_list_of_a_file,
                                                           practice)
    operations = [op.map(lambda x: x[1]),  # ignore the index, use the data
                  op.map(practice_reviewer),
                  op.to_list(),
                  op.map(lambda results: Series(results))]
    return reactive.iter_to_observable(df.iterrows()).pipe(*operations)


def practice_summary(practice_calif: Series):
    print("Media: {}, \n Dist: \n{}".format(practice_calif.mean(),
                                            practice_calif.groupby(practice_calif).agg('count')))