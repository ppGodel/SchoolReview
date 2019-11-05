from dataclasses import dataclass
from functools import partial
from typing import List, Dict, Callable

import pandas as pd

from src.reviewer.git_retrivers import get_repo_info


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
