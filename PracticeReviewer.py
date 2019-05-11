import re
from datetime import datetime
from typing import Callable

import pandas as pd
from functools import partial
from Students import RepositoryQuerier, get_response_content

score_function_type = Callable[[str, datetime, bytes], int]
practice_info = tuple[str, list[str], bool, score_function_type]


def read_csv(csv_path: str):
    students_df = pd.read_csv(csv_path)
    return students_df


def score_practice(practice_files: list[tuple[score_function_type, str, datetime, bytes]]) -> int:
    return sum([score_fn(p_name, p_date, p_file) for score_fn, p_name, p_date, p_file in practice_files])


def get_file_with_date(rq: RepositoryQuerier, repo_site: str, git_user: str, git_repo: str, practice_alias: str,
                       directory_allowed: bool) -> tuple[datetime, bytes]:
    file_info = search_file_in_repo_dir(rq, git_repo, git_user, repo_site, directory_allowed, "")
    file_date, file_raw = datetime(2010, 12, 31, 23, 59), None
    if file_info:
        commit_list_of_file = rq.get_commit_list_of_a_file(repo_site, git_user, git_repo, practice_alias)
        file_date = datetime.fromisoformat(commit_list_of_file[len(commit_list_of_file)]["commit"]["committer"]["date"])
        file_raw = get_response_content(file_info["download_url"])
    return file_date, file_raw


def search_file_in_repo_dir(rq: RepositoryQuerier, repo_site: str,  git_user: str, git_repo: str,
                            repo_dir: str, directory_allowed: bool) -> dict:
    files_info = rq.get_file_info(repo_site, git_user, git_repo, repo_dir)
    file_info_match = dict
    for file_info in files_info:
        matchObj = re.match( repo_dir, file_info["name"], re.M|re.I)
        if matchObj:
            if file_info["type"] == "dir":
                if directory_allowed:
                    file_info_match = file_info
                else:
                    file_info_match = search_file_in_repo_dir(rq,git_repo,git_user, repo_site)
            else:
                file_info_match = file_info
    return file_info_match


def get_files_with_date(rq: RepositoryQuerier, repo_site: str, git_user: str, git_repo: str,
                        practice_aliases: list[str], directory_allowed: bool) -> list[tuple[datetime, bytes]]:
    return [get_file_with_date(rq, repo_site, git_user, git_repo, practice_alias, directory_allowed) for practice_alias
            in
            practice_aliases]


def review_practice(rq: RepositoryQuerier, repo_site: str, git_user: str, git_repo: str,
                    practice: practice_info) -> pd.Series[int]:
    practice_name, practice_aliases, directory_allowed, score_function = practice
    info_files = [(score_function, practice_name, file_date, file_raw) for file_date, file_raw
                  in get_files_with_date(rq, repo_site, git_user, git_repo, practice_aliases, directory_allowed) if
                  file_date]
    return pd.Series(score_practice(info_files))


def check_practice(row: pd.Series, practice: practice_info) -> int:
    practice_name, practice_aliases, score_function = practice
    calif = -1
    try:
        calif = row[practice_name]
    except Exception as e:
        pass
    return calif


def check_and_review_practice(rq: RepositoryQuerier, row: pd.Series, practice: practice_info):
    calif = check_practice(row, practice)
    if not calif:
        calif = review_practice(rq, row.get("repo_site"), row.get("repo_user"), row.get("repo_name"), practice)
    return calif


def review_practice_from_df(df: pd.DataFrame, rq: RepositoryQuerier, practice: practice_info) -> pd.Series[int]:
    return df.apply(lambda row: check_and_review_practice(rq, row, practice), axis=1)
