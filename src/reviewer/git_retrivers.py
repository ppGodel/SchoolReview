import datetime
import urllib.parse
from functools import partial, lru_cache
from typing import Callable, Dict, List, Tuple, Optional, Union

import pandas as pd
import rx
from pandas import DataFrame, Series
from rx import operators as op

from src.Students import process_df, get_fn_with_credentials
from src.utils.url import get_response_content, get_response_json, get_url, map_parameters, get_base_url, \
    _remove_protocol_from_url
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


def github_get_repository_list_by(client_id: str, client_secret: str, site: str, user: str, prop: str) \
        -> Optional[List[str]]:
    repo_list = github_get_repository_list(client_id, client_secret, site, user)
    if not repo_list:
        return None
    try:
        return [x.get(prop) for x in repo_list]
    except AttributeError:
        print("site: {}, git_user: {}, property: {}".format(site,user,prop))


possible_repositories = dict(LDOO=["LDOO_EJ_19", "LDOO", "LDOO_EJ_2019", "LDOO_Enero_Julio_19",
                                   "LDOO_Enero_Julio_2019"],
                             LBD=['LBD', 'BD', 'BaseDeDatos'])


@lru_cache(maxsize=None)
def github_get_repository_list(client_id: str, client_secret: str, site: str, user: str) -> Dict:
    base_url = get_base_url("https://api.{site}/users/{user}/repos",
                            **{"site": site, "user": user})
    parameters = map_parameters(**{"client_id": client_id, "client_secret": client_secret})
    url = get_url(base_url, parameters)
    return get_response_json(url)


@lru_cache(maxsize=None)
def github_get_commit_list_of_a_file(client_id: str, client_secret: str, site, user, repo, file_path) -> List[Dict]:
    base_url = get_base_url("https://api.{site}/repos/{user}/{repo}/commits",
                            **{"site": site, "user": user, "repo": repo})
    parameters = map_parameters(
        **{"client_id": client_id, "client_secret": client_secret, "path": file_path})
    url = get_url(base_url, parameters)
    return get_response_json(url)


@lru_cache(maxsize=None)
def github_get_file_info(client_id: str, client_secret: str, site: str, user: str, repo: str, file_path: str) -> \
        Optional[Union[List[Dict], Dict]]:
    base_url = "https://api.{site}/repos/{user}/{repo}/contents/{file}". \
        format(site=site, user=user, repo=urllib.parse.quote(repo), file=urllib.parse.quote(file_path))
    parameters = map_parameters(**{"client_id": client_id, "client_secret": client_secret})
    url = get_url(base_url, parameters)
    return get_response_json(url)


def github_get_file(client_id: str, client_secret: str, site: str, user: str, repo: str, file_path: str) -> Optional[bytes]:
    file_info = None
    try:
        file_info = github_get_file_info(client_id, client_secret, site, user, repo, file_path)
    except Exception as e:
        print("Error found at get file from url {}".format(e))
    if not file_info:
        return None
    download_url = file_info['download_url']
    return get_response_content(download_url)


def get_querier(client_id: str, client_secret: str) -> Callable:
    return partial(get_fn_with_credentials, client_id, client_secret)


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