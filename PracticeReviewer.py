import re
from pandas import DataFrame, Series, read_csv
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Tuple
from Students import get_response_content

score_function_type = Callable[[str, datetime, bytes], int]


@dataclass
class Practice:
    name: str
    aliases: List[str]
    use_directory: bool
    score_function: score_function_type


def parse_csv_df(csv_path: str) -> DataFrame:
    students_df = read_csv(csv_path)
    return students_df


def review_practice_from_df(df: DataFrame, fn_get_file_info: Callable[[str, str, str, str], Dict],
                            fn_get_commit_list_of_a_file: Callable[[str, str, str, str], List[Dict]],
                            practice: Practice) -> Series[int]:
    return df.apply(
        lambda row: check_and_review_practice(fn_get_file_info, fn_get_commit_list_of_a_file, row, practice), axis=1)


def check_and_review_practice(fn_get_file_info: Callable[[str, str, str, str], Dict],
                              fn_get_commit_list_of_a_file: Callable[[str, str, str, str], List[Dict]],
                              row: Series, practice: Practice):
    calif = check_practice(row, practice)
    if not calif:
        calif = review_practice(fn_get_file_info, fn_get_commit_list_of_a_file, row.get("repo_site"),
                                row.get("repo_user"), row.get("repo_name"), practice)
    return calif


def check_practice(row: Series, practice: Practice) -> int:
    calif = -1
    try:
        calif = row[practice.name]
    except KeyError:
        pass
    return calif


def review_practice(fn_get_file_info: Callable[[str, str, str, str], Dict],
                    fn_get_commit_list_of_a_file: Callable[[str, str, str, str], List[Dict]],
                    repo_site: str, git_user: str, git_repo: str,
                    practice: Practice) -> Series[int]:
    practice_name, practice_aliases, directory_allowed, score_function = practice
    info_files = [(score_function, practice_name, file_date, file_raw) for file_date, file_raw
                  in get_files_with_date(fn_get_file_info, fn_get_commit_list_of_a_file, repo_site, git_user, git_repo,
                                         practice_aliases, directory_allowed) if
                  file_date]
    return Series(score_practice(info_files))


def score_practice(practice_files: List[Tuple[score_function_type, str, datetime, bytes]]) -> int:
    return sum([score_fn(p_name, p_date, p_file) for score_fn, p_name, p_date, p_file in practice_files])


def get_files_with_date(fn_get_file_info: Callable[[str, str, str, str], Dict],
                        fn_get_commit_list_of_a_file: Callable[[str, str, str, str], List[Dict]],
                        repo_site: str, git_user: str, git_repo: str,
                        practice_aliases: List[str], directory_allowed: bool) -> List[Tuple[datetime, bytes]]:
    return [get_file_with_date(fn_get_file_info, fn_get_commit_list_of_a_file, repo_site, git_user, git_repo,
                               practice_alias, directory_allowed) for practice_alias
            in
            practice_aliases]


def get_file_with_date(fn_get_file_info: Callable[[str, str, str, str], Dict],
                       fn_get_commit_list_of_a_file: Callable[[str, str, str, str], List[Dict]],
                       repo_site: str, git_user: str, git_repo: str, practice_alias: str, directory_allowed: bool) \
        -> Tuple[datetime, bytes]:
    file_info = search_file_in_repo_dir(fn_get_file_info, repo_site, git_user, git_repo, practice_alias, "", directory_allowed)
    file_date, file_raw = datetime(2010, 12, 31, 23, 59), None
    if file_info:
        commit_list_of_file = fn_get_commit_list_of_a_file(repo_site, git_user, git_repo, practice_alias)
        file_date = datetime.fromisoformat(
            commit_list_of_file[len(commit_list_of_file) - 1]["commit"]["committer"]["date"])
        file_raw = get_response_content(file_info["download_url"])
    return file_date, file_raw


def search_file_in_repo_dir(fn_get_file_info: Callable[[str, str, str, str], Dict], repo_site: str, git_user: str,
                            git_repo: str, practice_alias, repo_path: str, directory_allowed: bool) -> Dict:
    files_info = fn_get_file_info(repo_site, git_user, git_repo, repo_path)
    file_info_match = dict
    for file_info in files_info:
        match_obj = re.match(practice_alias, file_info["name"], re.M | re.I)
        if match_obj:
            if file_info["type"] == "dir":
                if directory_allowed:
                    file_info_match = file_info
                else:
                    file_info_match = search_file_in_repo_dir(fn_get_file_info, repo_site, git_user, git_repo,
                                                              practice_alias, file_info["path"], directory_allowed)
            else:
                file_info_match = file_info
    return file_info_match
