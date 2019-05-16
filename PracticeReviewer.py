import datetime
import json
import re
from functools import partial

from pandas import DataFrame, Series, read_csv
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Tuple, Optional, Union

from LBDReviews import create_repo_calif, practice_summary
from Students import get_response_content, get_querier, github_get_file_info, \
    github_get_commit_list_of_a_file
import cchardet


def convert_encoding(data: bytes, new_coding: str = 'UTF-8') -> bytes:
    encoding = cchardet.detect(data)['encoding']
    decoded_data = data.decode(encoding, data)
    if new_coding.upper() != encoding.upper():
        decoded_data = data.decode(encoding, data).encode(new_coding)
    return decoded_data


def convert_decoding(data: bytes) -> str:
    encoding = cchardet.detect(data)['encoding']
    decoded_data = data.decode(encoding, data)
    return decoded_data

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


def review_practice_from_df(df: DataFrame, fn_get_file_info: Callable[[str], Dict],
                            fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                            practice: Practice) -> Series:
    return df.apply(
        lambda row: check_and_review_practice(fn_get_file_info,
                                              fn_get_commit_list_of_a_file,
                                              row, practice), axis=1)


def check_and_review_practice(fn_get_file_info: Callable[[str, str, str], Dict],
                              fn_get_commit_list_of_a_file: Callable[[str, str, str], List[Dict]],
                              row: Series, practice: Practice) -> Optional[int]:
    calif = check_practice(row, practice)
    if calif is None or 0 < calif < 7:
        calif = review_practice(partial(fn_get_file_info,
                                        row.get("repo_site"),
                                        row.get("repo_user"),
                                        row.get("repo_name")),
                                partial(fn_get_commit_list_of_a_file,
                                        row.get("repo_site"),
                                        row.get("repo_user"),
                                        row.get("repo_name")),
                                practice)
    if not calif:
        calif = 0
    return calif


def check_practice(row: Series, practice: Practice) -> Optional[int]:
    calif = None
    try:
        if valid_row(row):
            calif = row[practice.name]
            if calif == -1:
                calif = 1
        else:
            calif = 0
    except KeyError:
        pass
    return calif


def valid_row(row: Series) -> bool:
    def check_column_value(column_value) -> bool:
        return column_value and column_value == column_value

    return check_column_value(row.get("repo_site")) \
           and check_column_value(row.get("repo_user")) \
           and check_column_value(row.get("repo_name"))


def review_practice(fn_get_file_info: Callable[[str], Dict],
                    fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                    practice: Practice) -> int:
    info_files = [(practice.score_function, practice.name, file_date, file_raw) for
                  file_date, file_raw
                  in get_files_with_date(fn_get_file_info, fn_get_commit_list_of_a_file,
                                         practice.aliases, practice.use_directory) if
                  file_date]
    return score_practice(info_files)


def score_practice(practice_files: List[Tuple[score_function_type, str, datetime, bytes]]) -> int:
    return sum(
        [score_fn(p_name, p_date, p_file) for score_fn, p_name, p_date, p_file in practice_files])


def get_files_with_date(fn_get_file_info: Callable[[str], Dict],
                        fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                        practice_aliases: List[str], directory_allowed: bool) -> List[
    Tuple[datetime, bytes]]:
    return [get_file_with_date(fn_get_file_info, fn_get_commit_list_of_a_file, practice_alias,
                               directory_allowed)
            for practice_alias in practice_aliases]


def get_file_with_date(fn_get_file_info: Callable[[str], Dict],
                       fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                       practice_alias: str, directory_allowed: bool) \
        -> Tuple[datetime, bytes]:
    file_info = search_in_repo_dir(fn_get_file_info, practice_alias, "", directory_allowed)
    file_date, file_raw = datetime(2010, 12, 31, 23, 59), None
    if file_info:
        commit_list_of_file = fn_get_commit_list_of_a_file(file_info["path"])
        last_commit_index = len(commit_list_of_file) - 1
        if last_commit_index >= 0:
            upload_date = commit_list_of_file[last_commit_index]["commit"]["committer"]["date"]
            file_date = datetime.strptime(upload_date, "%Y-%m-%dT%H:%M:%SZ")
        else:
            file_date = datetime.now()
        file_raw = get_response_content(file_info["download_url"])
    return file_date, file_raw


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
    except ConnectionError as ce:
        print(ce)
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


def review_class_by_practice(config_path:str, practice_info: Practice, csv_path:str):
    print("Reviewing: {} at {}".format(practice_info.name, datetime.datetime.now()))
    querier = get_querier_with_credentials(config_path)
    try:
        df_lbd = parse_csv_df(csv_path)
    except FileNotFoundError:
        df_lbd = create_repo_calif(querier, csv_path)
    practice_calif = review_practice_from_df(df_lbd, querier(github_get_file_info),
                                             querier(github_get_commit_list_of_a_file),
                                             practice_info)
    df_lbd[practice_info.name] = practice_calif
    df_lbd.to_csv(csv_path, sep=',', encoding='utf-8', index=False)
    practice_summary(practice_calif)
    print("Finish at {}".format(datetime.datetime.now()))


def practice_summary(practice_calif: Series):
    print("Media: {}, \n Dist: \n{}".format(practice_calif.mean(),
                                            practice_calif.groupby(practice_calif).agg('count')))