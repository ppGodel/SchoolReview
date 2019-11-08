import datetime
import json
from functools import partial
from typing import Callable, Dict, List, Tuple

import pandas as pd
import rx
from pandas import DataFrame, Series
from rx import operators as op

from Students import LBD, Student
from reviewer.PracticeReviewer import Practice, review_practice_from_df, \
    score_function_type, PracticeFile, get_practice_files, _check_and_review_practice
from reviewer.github_request_client import github_get_commit_list_of_a_file, github_get_file_info
from utils import reactive
from utils.pandas import parse_csv_df
from utils.url import remove_protocol_from_url, get_response_content


def review_practice_from_df_from_git(df: DataFrame, fn_get_file_info: Callable[[str], Dict],
                                     fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                                     get_file_content: Callable[[str], bytes],
                                     practice: Practice) -> Series:
    check_and_review_practice_from_row = check_and_review_practice_from_git(
        fn_get_file_info, fn_get_commit_list_of_a_file, get_file_content, practice)
    return review_practice_from_df(df, check_and_review_practice_from_row)


def get_practice_file_from_git(get_file_info: Callable[[str], Dict],
                               get_commit_list_of_a_file: Callable[[str], List[Dict]],
                               get_file_content: Callable[[str], bytes], practice: Practice) \
        -> List[Tuple[score_function_type,
                                                                 str, PracticeFile]]:
    return [(practice.score_function, practice.name, practice_file_info) for practice_file_info in
            get_practice_files(get_file_info, get_commit_list_of_a_file, get_file_content,
                               practice.aliases, practice.as_dir) if practice_file_info]


def check_and_review_practice_from_git(fn_get_file_info: Callable[[str, str, str], Dict],
                                       fn_get_commit_list_of_a_file:
                                       Callable[[str, str, str, str], List[Dict]],
                                       get_file_content: Callable[[str], bytes],
                                       practice: Practice) -> Callable[[Series], int]:
    def _check_and_review_practice_from_git(row: Series) -> int:
        get_file = partial(fn_get_file_info, row.get("repo_site"), row.get("repo_user"), row.get("repo_name"))
        get_commit_list = partial(fn_get_commit_list_of_a_file, row.get("repo_site"), row.get("repo_user"),
                                  row.get("repo_name"))
        get_practice_list = partial(get_practice_file_from_git, get_file, get_commit_list, get_file_content)
        return _check_and_review_practice(get_practice_list, row, practice)

    return _check_and_review_practice_from_git


def review_class_by_practice(config_path: str, practice_info: Practice, target_csv_path: str,
                             base_csv_path: str,
                             create_repo_calif_df: Callable[[Callable, str, str], DataFrame]):
    querier = get_querier_with_credentials(config_path)
    try:
        df_lbd = parse_csv_df(target_csv_path)
    except FileNotFoundError:
        df_lbd = create_repo_calif_df(querier, base_csv_path, target_csv_path)
    practice_calif = review_practice_from_df_from_git(df_lbd, querier(github_get_file_info),
                                                      querier(github_get_commit_list_of_a_file),
                                                      get_response_content,
                                                      practice_info)
    df_lbd[practice_info.name] = practice_calif
    df_lbd.to_csv(target_csv_path, sep=',', encoding='utf-8', index=False)
    practice_summary(practice_calif)


class DFSaver(rx.core.Observer):
    def __init__(self, df: DataFrame):
        self.df = df  # type: DataFrame
        self.practice_results = []  # type: List[Tuple[str,Series]]

    def on_next(self, practice_results: Tuple[str, Series]):
        self.practice_results = self.practice_results + [practice_results]

    def on_complete(self):
        self.df = self.df.assign(**dict(self.practice_results))


def rx_review_practice_from_df(df: DataFrame, fn_get_file_info: Callable[[str, str, str], Dict],
                               fn_get_commit_list_of_a_file: Callable[[str, str, str, str], List[Dict]],
                               get_file_content: Callable[[str], bytes],
                               practice: Practice) -> rx.Observable:
    practice_reviewer = check_and_review_practice_from_git(fn_get_file_info, fn_get_commit_list_of_a_file,
                                                           get_file_content, practice)
    operations = [op.map(lambda x: x[1]),  # ignore the index, use the data
                  op.map(practice_reviewer),
                  op.to_list(),
                  op.map(lambda results: {practice.name: Series(results)})]
    return reactive.iter_to_observable(df.iterrows()).pipe(*operations)


def practice_summary(practice_calif: Series):
    print("Media: {}, \n Dist: \n{}".format(practice_calif.mean(),
                                            practice_calif.groupby(practice_calif).agg('count')))


def build_course_from_csv(
        get_repo_list_by: Callable[[str, str, str], List[Dict]],
        csv_path: str, git_column: str,
        base_column_names: List, new_column_names: List):
    students_df = pd.read_csv(csv_path)
    dfr = process_df(get_repo_list_by, students_df, git_column)
    dfr.columns = ['repo_site', 'repo_user', 'repo_name']
    base_df = students_df.loc[:, base_column_names]
    base_df.rename(columns=dict(zip(base_column_names, new_column_names)), inplace=True)
    new_df = pd.concat([base_df, dfr], axis=1)
    return new_df


possible_repositories = dict(LDOO=["LDOO_EJ_19", "LDOO", "LDOO_EJ_2019", "LDOO_Enero_Julio_19",
                                   "LDOO_Enero_Julio_2019"],
                             LBD=['LBD', 'BD', 'BaseDeDatos'])


def get_querier(client_id: str, client_secret: str) -> Callable:
    return partial(get_fn_with_credentials, client_id, client_secret)


def get_repo_info(get_repolist_map_by: Callable[[str, str, str], List[Dict]], url: str, class_name: str) \
        -> Tuple[str, str, str]:
    site = user = repo = None
    try:
        base_url = remove_protocol_from_url(url)
        url_pieces = base_url.split('/')
        pieces = len(url_pieces)
        if pieces > 1 and url_pieces[0] and url_pieces[1]:
            site = _format_site(url_pieces[0])
            user = url_pieces[1]
            if pieces > 2 and url_pieces[2]:
                repo = _format_repo(url_pieces[2])
    except Exception as e:
        print("No valid repo for {}, {}".format(url, e))
    return validate_repository(get_repolist_map_by, site, user, repo, class_name)


def validate_repository(get_repolist_map_by: Callable[[str, str, str], List[Dict]], site, user, repo, class_name) \
        -> Tuple[str, str, str]:
    validated_site = validated_user = validated_repo = repo_list = None
    if site and user:
        repo_list = get_repolist_map_by(site, user, 'name')
    if repo_list:
        validated_site = site
        validated_user = user
        validated_repo = repo if repo in repo_list else \
            search_valid_repository(class_name, repo_list)
    return validated_site, validated_user, validated_repo


def search_valid_repository(class_name, repo_list):
    validated_repo = None
    for x in possible_repositories.get(class_name):
        if x in repo_list:
            validated_repo = x
            break
    return validated_repo


def _format_repo(repo_raw: str):
    repo_pieces = repo_raw.split('.')
    return repo_pieces[0]


def _format_site(site):
    formatted_site = None
    site_pieces = site.split('.')
    sp_len = len(site_pieces)
    if sp_len > 1:
        formatted_site = site_pieces[sp_len - 2] + '.' + site_pieces[sp_len - 1]
    return formatted_site


def get_fn_with_credentials(client_id: str, client_secret: str, function: Callable) -> Callable:
    return partial(function, client_id, client_secret)


def process_df(get_repo_list_by: Callable[[str, str, str], List[Dict]], students_df: pd.DataFrame, git_column: str):
    return students_df.apply(
        lambda row: get_repo_info(get_repo_list_by, row.get(git_column), LBD),
        axis='columns', result_type='expand')


def build_student(get_repolist_map_by: Callable[[str, str, str], List[Dict]], matricula: str, class_name: str,
                  url: str) -> Student:
    site, user, repo, = get_repo_info(get_repolist_map_by, url, class_name)
    return Student(matricula, class_name, site, user, repo) if site and user else None


def get_querier_with_credentials(config_path: str):
    with open(config_path) as f:
        my_data = json.load(f)
    return get_querier(my_data["client_id"], my_data["client_secret"])
