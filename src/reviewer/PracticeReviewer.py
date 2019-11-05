import datetime
import json
import re
from functools import reduce
import numpy as np
from pandas import DataFrame, Series
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Tuple, Optional, Union
from src.Students import get_response_content, get_querier


@dataclass
class PracticeFile:
    name: str
    deliver_date: datetime
    file_path: str
    file_raw: bytes
    file_info: List[Dict]


score_function_type = Callable[[str, PracticeFile], int]


@dataclass
class Practice:
    name: str
    aliases: List[str]
    as_dir: bool
    score_function: score_function_type


def _check_and_review_practice(get_practice_list: Callable[[Practice],
                                                           List[Tuple[score_function_type,
                                                                      str, PracticeFile]]],
                               row: Series, practice: Practice):
    practice_list = get_practice_list(practice)
    return check_and_review_practice(practice_list, row, practice)


def review_practice_from_df(df: DataFrame, fn_check_and_review_row: Callable[[Series], int]) \
        -> Series:
    return df.apply(lambda row: fn_check_and_review_row(row), axis=1)


def check_and_review_practice(practice_list: List[Tuple[score_function_type, str, PracticeFile]],
                              row: Series, practice: Practice) -> Optional[int]:
    calif = check_practice(row, practice.name)
    if calif is None or 0 < calif < 7:
        calif = score_practice(practice_list)
    if not calif:
        calif = 0
    return calif


def check_practice(row: Series, practice_name: str) -> Optional[int]:
    calif = None
    try:
        if valid_row(row, ['repo_site', 'repo_user', 'repo_name']):
            calif = row[practice_name]
            if calif == -1:
                calif = 1
        else:
            calif = 0
    except KeyError:
        pass
    return calif


def valid_row(row: Series, required_values: List[str]) -> bool:
    def check_column_value(column_value) -> bool:
        return not np.isnan(column_value) \
               and column_value is not None and column_value != ''

    return reduce(lambda x1, x2: x1 and x2,
                  [check_column_value(row.get(column_value, None))
                   for column_value in required_values], True)


def score_practice(practice_files: List[Tuple[score_function_type, str, PracticeFile]]) -> int:
    scores = []
    for score_fn, p_name, p_file_info in practice_files:
        score = score_fn(practice_name=p_name, file=p_file_info)
        scores.append(score)
    return max(scores, default=0)


def get_practice_files(fn_get_file_info: Callable[[str], Dict],
                       fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                       practice_aliases: List[str], practice_as_dir: bool) -> List[PracticeFile]:
    return [
        search_practice_files_in_git(fn_get_file_info, fn_get_commit_list_of_a_file, practice_alias, practice_as_dir)
        for practice_alias in practice_aliases]


def search_practice_files_in_git(fn_get_file_info: Callable[[str], Dict],
                                 fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                                 practice_alias: str, practice_as_dir: bool) \
        -> PracticeFile:
    file_description = search_in_repo_dir(fn_get_file_info, practice_alias, "", practice_as_dir)
    file_name, file_date, file_path, file_raw, file_info = None, datetime(2010, 12, 31, 23, 59), None, None, []
    if file_description:
        commit_list_of_file = fn_get_commit_list_of_a_file(file_description["path"])
        last_commit_index = len(commit_list_of_file) - 1
        if last_commit_index >= 0:
            upload_date = commit_list_of_file[last_commit_index]["commit"]["committer"]["date"]
            file_name = file_description["name"]
            file_path = file_description["path"]
            file_date = datetime.strptime(upload_date, "%Y-%m-%dT%H:%M:%SZ")
            if file_description["download_url"]:
                file_raw = get_response_content(file_description["download_url"])
                file_info.append(file_description)
            else:
                try:
                    file_info = [dict(name=file["name"], path=file["path"], download_url=file["download_url"]) for file
                                 in fn_get_file_info(file_path)]
                except TypeError:
                    print("Error getting path {}".format(file_path))
        else:
            file_date = datetime.now()
    return PracticeFile(file_name, file_date, file_path, file_raw, file_info)


def search_in_repo_dir(fn_get_file_info_from_path: Callable[[str], Dict], practice_alias,
                       repo_path: str, directory_allowed: bool) \
        -> Optional[Union[List[Dict], Dict]]:
    file_info_match = search_dir_in_repo_dir(fn_get_file_info_from_path, practice_alias, repo_path)
    if not directory_allowed:
        if not file_info_match:
            file_info_match = search_file_in_repo_dir(fn_get_file_info_from_path, practice_alias,
                                                      repo_path)
        else:
            file_info_match = search_file_in_repo_dir(fn_get_file_info_from_path, practice_alias,
                                                      file_info_match["path"])
    return file_info_match


def search_file_in_repo_dir(fn_get_file_info_from_path: Callable[[str], Dict], practice_alias: str,
                            repo_path: str) -> Optional[Dict]:
    files_info = fn_get_file_info_from_path(repo_path)
    file_info_match = None
    for file_info in files_info:
        try:
            file_name = file_info["name"].strip()
        except TypeError:
            continue
        match_obj = re.search(practice_alias, file_name, re.M | re.I)
        if match_obj:
            if file_info["type"] == "dir":
                file_info_match = search_file_in_repo_dir(fn_get_file_info_from_path,
                                                          practice_alias,
                                                          file_info["path"])
            else:
                file_info_match = file_info
                break
    return file_info_match


def search_dir_in_repo_dir(fn_get_file_info_from_path: Callable[[str], Dict], practice_alias: str,
                           repo_path: str) -> Optional[Dict]:
    try:
        files_info = [file for file in fn_get_file_info_from_path(repo_path) if
                      file["type"] == "dir"]
    except Exception:
        print("Path info not found: {}".format(repo_path))
        files_info = []
    file_info_match = None
    for file_info in files_info:
        match_obj = re.search(practice_alias, file_info["name"].strip(), re.M | re.I)
        if match_obj:
            file_info_match = file_info
            break
    return file_info_match


def get_querier_with_credentials(config_path: str):
    with open(config_path) as f:
        my_data = json.load(f)
    return get_querier(my_data["client_id"], my_data["client_secret"])
