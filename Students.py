import re
from dataclasses import dataclass
from functools import partial
from typing import Tuple, List, Dict, Callable

import pandas as pd


@dataclass
class Student:
    student_id: str
    class_name: str
    git_site: str
    git_user: str
    git_repo: str


LDOO = 'LDOO'
LBD = 'LBD'
name = 'Name'

possible_repositories = dict(LDOO=["LDOO_EJ_19", "LDOO", "LDOO_EJ_2019", "LDOO_Enero_Julio_19",
                                   "LDOO_Enero_Julio_2019"],
                             LBD=['LBD', 'BD', 'BaseDeDatos'])


def get_fn_with_credentials(client_id: str, client_secret: str, function: Callable) -> Callable:
    return partial(function, client_id, client_secret)


def get_querier(client_id: str, client_secret: str) -> Callable:
    return partial(get_fn_with_credentials, client_id, client_secret)


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


def process_df(get_repo_list_by: Callable[[str, str, str], List[Dict]], students_df: pd.DataFrame, git_column: str):
    return students_df.apply(
        lambda row: get_repo_info(get_repo_list_by, row.get(git_column), LBD),
        axis='columns', result_type='expand')


def build_student(get_repolist_map_by: Callable[[str, str, str], List[Dict]], matricula: str, class_name: str,
                  url: str) -> Student:
    site, user, repo, = get_repo_info(get_repolist_map_by, url, class_name)
    return Student(matricula, class_name, site, user, repo) if site and user else None


def get_repo_info(get_repolist_map_by: Callable[[str, str, str], List[Dict]], url: str, class_name: str) \
        -> Tuple[str, str, str]:
    site = user = repo = None
    try:
        base_url = _remove_protocol_from_url(url)
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


def _remove_protocol_from_url(url: str):
    return_url = url
    is_match = re.match('https?://', url)
    if is_match:
        return_url = url.replace(is_match.group(0), '')
    return return_url


