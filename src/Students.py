import re
from dataclasses import dataclass
from functools import partial, lru_cache
from typing import Optional, Union, Tuple, List, Dict, Callable

import pandas as pd
import requests
import urllib.parse


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


def github_get_repository_list_by(client_id: str, client_secret: str, site: str, user: str, prop: str) \
        -> Optional[List[str]]:
    repo_list = github_get_repository_list(client_id, client_secret, site, user)
    if not repo_list:
        return None
    try:
        return [x.get(prop) for x in repo_list]
    except AttributeError:
        print("site: {}, git_user: {}, property: {}".format(site,user,prop))


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


@lru_cache(maxsize=None)
def get_response_content(download_url) -> bytes:
    content = None
    response = requests.get(download_url)
    if response.status_code >= 200 <= 250:
        content = response.content
    return content


@lru_cache(maxsize=None)
def get_response_json(url) -> Optional[Union[Dict, List[Dict]]]:
    response = requests.get(url)
    json = None
    if response.status_code >= 200 <= 250:
        json = response.json()
    return json


def get_url(base_url: str, params: str):
    return "{base}?{parameters}".format(base=base_url, parameters=params)


def map_parameters(**params):
    parameters = None
    if params:
        parameters = "&".join([f"{urllib.parse.quote(k)}={urllib.parse.quote(v)}" for (k, v) in params.items()])
    return parameters


def get_base_url(url_template: str, **kwargs):
    return url_template.format(**kwargs)

# def review_student_practice(repo_site: str, repo_user: str, repo_name: str, practice_obj: dict):
#     p_due_date = datetime.datetime.strptime(practice_obj.get('due_date'), "%Y-%m-%d %H:%M")
#     calif = None
#     file_name = None
#     commit_list = None
#     for poss_name in practice_obj.get('possible_name'):
#         commit_list = RepositoryQuerier.get_commit_list_of_a_file(repo_site, repo_user, repo_name, poss_name)
#         if commit_list:
#             file_name = poss_name
#             break
#     if not commit_list:
#         if datetime.datetime.now() < p_due_date:
#             return calif
#         else:
#             return 0
#     first_commit = commit_list[len(commit_list) - 1]['commiter']['date']
#     first_commit_date = datetime.datetime.strptime(first_commit, "%Y-%m-%dT%H:%M:%sZ")
#     if first_commit_date < p_due_date:
#         calif = practice_obj.get('due_value')
#     else:
#         calif = 0
#     # eval_list = practice_obj.get('review_rules')
#     # file_to_review = RepositoryQuerier.get_file(repo_site,repo_user, repo_name, file_name)
#     # for eval_rule in eval_list:
#     #    matches = re.search(eval_rule.get('regex'), file_to_review)
#     #    if matches:
#     #        eval_code = matches.group(eval_rule.get('group'))
#     #        eval_code.split(',')
#     return calif
#
#
# def review_practice(students_df: pd.DataFrame, practice_dict: dict):
#     return_value = students_df.apply(lambda row: review_student_practice(
#         row.get('repo_site', 'repo_user', 'repo_name'), practice_dict),
#                                      axis='columns', result_type='expand')
#     return return_value
