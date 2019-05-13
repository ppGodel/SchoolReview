import re
from functools import partial

from pandas import DataFrame, Series, read_csv
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Tuple, Optional, Union
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


def review_practice_from_df(df: DataFrame, fn_get_file_info: Callable[[str], Dict],
                            fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                            practice: Practice) -> Series:
    return df.apply(
        lambda row: check_and_review_practice(partial(fn_get_file_info,
                                                      row.get("repo_site"),
                                                      row.get("repo_user"),
                                                      row.get("repo_name")),
                                              partial(fn_get_commit_list_of_a_file,
                                                      row.get("repo_site"),
                                                      row.get("repo_user"),
                                                      row.get("repo_name")),
                                              row, practice), axis=1)


def check_and_review_practice(fn_get_file_info: Callable[[str], Dict],
                              fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                              row: Series, practice: Practice) -> Optional[int]:
    calif = check_practice(row, practice)
    if not calif or calif < 0:
        calif = review_practice(fn_get_file_info, fn_get_commit_list_of_a_file, practice)
    if not calif:
        calif = -1
    return calif


def check_practice(row: Series, practice: Practice) -> Optional[int]:
    calif = None
    try:
        calif = row[practice.name]
    except KeyError:
        pass
    return calif


def review_practice(fn_get_file_info: Callable[[str], Dict],
                    fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                    practice: Practice) -> int:
    info_files = [(practice.score_function, practice.name, file_date, file_raw) for file_date, file_raw
                  in get_files_with_date(fn_get_file_info, fn_get_commit_list_of_a_file,
                                         practice.aliases, practice.use_directory) if
                  file_date]
    return score_practice(info_files)


def score_practice(practice_files: List[Tuple[score_function_type, str, datetime, bytes]]) -> int:
    return sum([score_fn(p_name, p_date, p_file) for score_fn, p_name, p_date, p_file in practice_files])


def get_files_with_date(fn_get_file_info: Callable[[str], Dict],
                        fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                        practice_aliases: List[str], directory_allowed: bool) -> List[Tuple[datetime, bytes]]:
    return [get_file_with_date(fn_get_file_info, fn_get_commit_list_of_a_file, practice_alias, directory_allowed)
            for practice_alias in practice_aliases]


def get_file_with_date(fn_get_file_info: Callable[[str], Dict],
                       fn_get_commit_list_of_a_file: Callable[[str], List[Dict]],
                       practice_alias: str, directory_allowed: bool) \
        -> Tuple[datetime, bytes]:
    file_info = search_in_repo_dir(fn_get_file_info, practice_alias, "", directory_allowed)
    file_date, file_raw = datetime(2010, 12, 31, 23, 59), None
    if file_info:
        commit_list_of_file = fn_get_commit_list_of_a_file(file_info["name"])
        upload_date = commit_list_of_file[len(commit_list_of_file) - 1]["commit"]["committer"]["date"]
        file_date = datetime.strptime(upload_date, "%Y-%m-%dT%H:%M:%SZ")
        file_raw = get_response_content(file_info["download_url"])
    return file_date, file_raw


def search_in_repo_dir(fn_get_file_info_from_path: Callable[[str], Dict], practice_alias,
                       repo_path: str, directory_allowed: bool) \
        -> Optional[Union[List[Dict], Dict]]:
    file_info_match = search_dir_in_repo_dir(fn_get_file_info_from_path, practice_alias, repo_path)
    if not directory_allowed:
        if not file_info_match:
            file_info_match = search_file_in_repo_dir(fn_get_file_info_from_path, practice_alias, repo_path)
        else:
            file_info_match = search_file_in_repo_dir(fn_get_file_info_from_path, practice_alias,
                                                      file_info_match["path"])
    return file_info_match


def search_file_in_repo_dir(fn_get_file_info_from_path: Callable[[str], Dict], practice_alias: str,
                            repo_path: str) -> Optional[Dict]:
    files_info = fn_get_file_info_from_path(repo_path)
    file_info_match = None
    for file_info in files_info:
        match_obj = re.match(practice_alias, file_info["name"].strip(), re.M | re.I)
        if match_obj:
            if file_info["type"] == "dir":
                file_info_match = search_file_in_repo_dir(fn_get_file_info_from_path, practice_alias,
                                                          file_info["path"])
            else:
                file_info_match = file_info
    return file_info_match


def search_dir_in_repo_dir(fn_get_file_info_from_path: Callable[[str], Dict], practice_alias: str,
                           repo_path: str) -> Optional[Dict]:
    files_info = [file for file in fn_get_file_info_from_path(repo_path) if file["type"] == "dir"]
    file_info_match = None
    for file_info in files_info:
        match_obj = re.match(practice_alias, file_info["name"].strip(), re.M | re.I)
        if match_obj:
            file_info_match = file_info
    return file_info_match


def score_practice_1_lbd(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    start_date = datetime(2019, 2, 9, 00, 00)
    limit_date = datetime(2019, 3, 2, 23, 59)
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if file and len(file) > 10:
        score = score + 7
    return score


def score_practice_2_lbd(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    start_date = datetime(2019, 2, 16, 00, 00)
    limit_date = datetime(2019, 3, 9, 23, 59)
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if len(file) > 10:
        score = score + 7
    return score


def score_practice_3_lbd(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    start_date = datetime(2019, 2, 25, 00, 00)
    limit_date = datetime(2019, 3, 16, 23, 59)
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if len(file) > 10:
        score = score + 7
    return score


def score_practice_4_lbd(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    start_date = datetime(2019, 3, 2, 00, 00)
    limit_date = datetime(2019, 3, 25, 23, 59)
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if len(file) > 10:
        score = score + 7
    return score


def score_practice_5_lbd(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    start_date = datetime(2019, 3, 9, 00, 00)
    limit_date = datetime(2019, 4, 2, 23, 59)
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if len(file) > 10:
        score = score + 7
    return score


lbd_p1 = Practice("Practica1", [r"P(r(a|á)ctica)\s*0?1", r"T(area)?\s*0?1"], False, score_practice_1_lbd)
lbd_p2 = Practice("Practica1", [r"P(r(a|á)ctica)\s*0?2", r"T(area)?\s*0?2"], False, score_practice_2_lbd)
lbd_p3 = Practice("Practica1", [r"P(r(a|á)ctica)\s*0?3", r"T(area)?\s*0?3"], False, score_practice_3_lbd)
lbd_p4 = Practice("Practica1", [r"P(r(a|á)ctica)\s*0?4", r"T(area)?\s*0?4"], False, score_practice_4_lbd)
lbd_p5 = Practice("Practica1", [r"P(r(a|á)ctica)\s*0?5", r"T(area)?\s*0?5"], False, score_practice_5_lbd)
