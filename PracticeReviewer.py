import re
from functools import partial

from numpy import NaN
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
        match_obj = re.match(practice_alias, file_info["name"].strip(), re.M | re.I)
        if match_obj:
            if file_info["type"] == "dir":
                file_info_match = search_file_in_repo_dir(fn_get_file_info_from_path,
                                                          practice_alias,
                                                          file_info["path"])
            else:
                file_info_match = file_info
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
    end_date = datetime(2019, 4, 28, 0, 0)
    if delivery_date > end_date:
        return 0
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if file:
        reg_ex = b"(create\s+table\s+(\[?\w+\]?\.?)+)"
        match_obj = re.findall(reg_ex, file, re.M | re.I)
        points = 0
        if match_obj:
            created_tables = len(match_obj)
            score = score + (7 * min(created_tables / 5, 1))
    return score


def score_practice_3_lbd(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    start_date = datetime(2019, 2, 23, 00, 00)
    limit_date = datetime(2019, 3, 16, 23, 59)
    end_date = datetime(2019, 4, 28, 0, 0)
    if delivery_date > end_date:
        return 0
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if file and len(file) > 10:
        score = score + 7
    return score


def score_practice_4_lbd(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    start_date = datetime(2019, 3, 2, 00, 00)
    limit_date = datetime(2019, 3, 23, 23, 59)
    end_date = datetime(2019, 4, 28, 0, 0)
    if delivery_date > end_date:
        return 0
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if file and len(file) > 10:
        score = score + 7
    return score


def score_practice_5_lbd(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    start_date = datetime(2019, 3, 9, 00, 00)
    limit_date = datetime(2019, 3, 30, 23, 59)
    end_date = datetime(2019, 4, 28, 0, 0)
    if delivery_date > end_date:
        return 0
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if file:
        reg_ex = b"(insert\s+\w+)"
        match_obj = re.findall(reg_ex, file, re.M | re.I)
        points = 0
        if match_obj:
            inserts = len(match_obj)
            score = score + (5 * min(inserts / 100, 1))
        reg_ex = b"(update\s+\w+)"
        match_obj = re.findall(reg_ex, file, re.M | re.I)
        points = 0
        if match_obj:
            updates = len(match_obj)
            score = score + (1 * min(updates / 5, 1))

        reg_ex = b"(delete\s+\w+)"
        match_obj = re.findall(reg_ex, file, re.M | re.I)
        points = 0
        if match_obj:
            deletes = len(match_obj)
            score = score + (1 * min(deletes / 5, 1))
    return score


def score_practice_6_lbd(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    start_date = datetime(2019, 3, 16, 00, 00)
    limit_date = datetime(2019, 4, 6, 23, 59)
    end_date = datetime(2019, 4, 28, 0, 0)
    if delivery_date > end_date:
        return 0
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if file:
        reg_ex = b"(select\s+\w+)"
        match_obj = re.findall(reg_ex, file, re.M | re.I)
        points = 0
        if match_obj:
            inserts = len(match_obj)
            score = score + (7 * min(inserts / 15, 1))
    return score


def score_practice_7_lbd(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    start_date = datetime(2019, 3, 23, 00, 00)
    limit_date = datetime(2019, 4, 13, 23, 59)
    end_date = datetime(2019, 4, 28, 0, 0)
    if delivery_date > end_date:
        return 0
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if file:
        reg_ex = b"(create\s+view\s+(\[?\w+\]?\.?)+)"
        match_obj = re.findall(reg_ex, file, re.M | re.I)
        points = 0
        if match_obj:
            inserts = len(match_obj)
            score = score + (7 * min(inserts / 5, 1))
    return score


def score_practice_8_lbd(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    start_date = datetime(2019, 3, 30, 00, 00)
    limit_date = datetime(2019, 4, 20, 23, 59)
    end_date = datetime(2019, 4, 28, 0, 0)
    if delivery_date > end_date:
        return 0
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if file:
        reg_ex = b"(create\s+trigger\s+(\[?\w+\]?\.?)+)"
        match_obj = re.findall(reg_ex, file, re.M | re.I)
        points = 0
        if match_obj:
            inserts = len(match_obj)
            score = score + (2 * min(inserts / 1, 1))
        reg_ex = b"(create\s+(stored\s+)?procedure\s+(\[?\w+\]?\.?)+)"
        match_obj = re.findall(reg_ex, file, re.M | re.I)
        points = 0
        if match_obj:
            inserts = len(match_obj)
            score = score + (3 * min(inserts / 5, 1))
        reg_ex = b"(create\s+function\s+(\[?\w+\]?\.?)+)"
        match_obj = re.findall(reg_ex, file, re.M | re.I)
        points = 0
        if match_obj:
            inserts = len(match_obj)
            score = score + (2 * min(inserts / 1, 1))
    return score



def score_pia_lbd(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    start_date = datetime(2019, 3, 30, 00, 00)
    limit_date = datetime(2019, 4, 20, 23, 59)
    end_date = datetime(2019, 4, 28, 0, 0)
    if delivery_date > end_date:
        return 0
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if file and len(file) > 10:
        score = score + 7
    return score * 2


lbd_p1 = Practice("Practica1", [r"P(r(a|á)ctica)?(\s*|_*)(0?1|uno)",
                                r"T(area)?(\s*|_*)(0?1|uno)"], False, score_practice_1_lbd)
lbd_p2 = Practice("Practica2", [r"P(r(a|á)ctica)?(\s*|_*)(0?2|dos)",
                                r"T(area)?(\s*|_*)(0?2|dos)"], False, score_practice_2_lbd)
lbd_p3 = Practice("Practica3", [r"P(r(a|á)ctica)?(\s*|_*)(0?3|tres)",
                                r"T(area)?(\s*|_*)(0?3|tres)"], False, score_practice_3_lbd)
lbd_p4 = Practice("Practica4", [r"P(r(a|á)ctica)?(\s*|_*)(0?4|cuatro)",
                                r"T(area)?(\s*|_*)(0?4|cuatro)"], False, score_practice_4_lbd)
lbd_p5 = Practice("Practica5", [r"P(r(a|á)ctica)?(\s*|_*)(0?5|cinco)",
                                r"T(area)?(\s*|_*)(0?5|cinco)"], False, score_practice_5_lbd)
lbd_p6 = Practice("Practica6", [r"P(r(a|á)ctica)?(\s*|_*)(0?6|seis)",
                                r"T(area)?(\s*|_*)(0?6|seis)"], False, score_practice_6_lbd)
lbd_p7 = Practice("Practica7", [r"P(r(a|á)ctica)?(\s*|_*)(0?7|siete)",
                                r"T(area)?(\s*|_*)(0?7|siete)"], False, score_practice_7_lbd)
lbd_p8 = Practice("Practica8", [r"P(r(a|á)ctica)?(\s*|_*)(0?8|ocho)",
                                r"T(area)?(\s*|_*)(0?8|ocho)"], False, score_practice_8_lbd)
lbd_pia = Practice("PIA", [r"P(r(a|á)ctica)?(\s*|_*)(0?8|ocho)",
                                r"T(area)?(\s*|_*)(0?8|ocho)"], False, score_pia_lbd)
