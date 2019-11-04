import datetime
from datetime import datetime
from functools import partial
from typing import Callable

from src.reviewer.PracticeReviewer import Practice, PracticeFile
from practice_re import p1_re, p2_re, p3_re, p4_re, p5_re, p6_re, p7_re, p8_re, pia_re


def score_practice_1_lbd(practice_name: str, file: PracticeFile) -> int:
    score = 0
    if not file or exceds_end_date(file.deliver_date):
        return 0
    start_date = datetime(2019, 2, 9, 00, 00)
    limit_date = datetime(2019, 3, 2, 23, 59)
    if start_date <= file.deliver_date <= limit_date:
        score = score + 3
    if file.file_raw and len(file.file_raw) > 10:
        score = score + 7
    return score


def score_practice_2_lbd(practice_name: str, file: PracticeFile) -> int:
    score = 0
    if not file or exceds_end_date(file.deliver_date):
        return 0
    start_date = datetime(2019, 2, 16, 00, 00)
    limit_date = datetime(2019, 3, 9, 23, 59)
    if start_date <= file.deliver_date <= limit_date:
        score = score + 3
    if file.file_raw and len(file.file_raw) > 10:
        score = score + 7
    # if file:
    #     reg_ex = b"(create(\s|\t|\n)+table(\s|\t|\n)+(\[?\w+\]?\.?)+)"
    #     match_obj = re.findall(reg_ex, file, re.M | re.I)
    #     points = 0
    #     if match_obj:
    #         created_tables = len(match_obj)
    #         score = score + (7 * min(created_tables / 5, 1))
    return score


def score_practice_3_lbd(practice_name: str, file: PracticeFile) -> int:
    score = 0
    if not file or exceds_end_date(file.deliver_date):
        return 0
    start_date = datetime(2019, 2, 23, 00, 00)
    limit_date = datetime(2019, 3, 16, 23, 59)
    if start_date <= file.deliver_date <= limit_date:
        score = score + 3
    if file.file_raw and len(file.file_raw) > 10:
        score = score + 7
    return score


def score_practice_4_lbd(practice_name: str, file: PracticeFile) -> int:
    score = 0
    if not file or exceds_end_date(file.deliver_date):
        return 0
    start_date = datetime(2019, 3, 2, 00, 00)
    limit_date = datetime(2019, 3, 23, 23, 59)
    if start_date <= file.deliver_date <= limit_date:
        score = score + 3
    if file.file_raw and len(file.file_raw) > 10:
        score = score + 7
    return score


def score_practice_5_lbd(practice_name: str, file: PracticeFile) -> int:
    score = 0
    if not file or exceds_end_date(file.deliver_date):
        return 0
    start_date = datetime(2019, 3, 9, 00, 00)
    limit_date = datetime(2019, 3, 30, 23, 59)
    if start_date <= file.deliver_date <= limit_date:
        score = score + 3
    if file.file_raw and len(file.file_raw) > 10:
        score = score + 7
    # if file:
    #     reg_ex = b"(insert(\s|\t|\n)+\w+)"
    #     match_obj = re.findall(reg_ex, file, re.M | re.I)
    #     points = 0
    #     if match_obj:
    #         inserts = len(match_obj)
    #         score = score + (5 * min(inserts / 100, 1))
    #     reg_ex = b"(update(\s|\t|\n)+\w+)"
    #     match_obj = re.findall(reg_ex, file, re.M | re.I)
    #     points = 0
    #     if match_obj:
    #         updates = len(match_obj)
    #         score = score + (1 * min(updates / 5, 1))
    #
    #     reg_ex = b"(delete(\s|\t|\n)+\w+)"
    #     match_obj = re.findall(reg_ex, file, re.M | re.I)
    #     points = 0
    #     if match_obj:
    #         deletes = len(match_obj)
    #         score = score + (1 * min(deletes / 5, 1))
    return score


def score_practice_6_lbd(practice_name: str, file: PracticeFile) -> int:
    score = 0
    if not file or exceds_end_date(file.deliver_date):
        return 0
    start_date = datetime(2019, 3, 16, 00, 00)
    limit_date = datetime(2019, 4, 6, 23, 59)
    if start_date <= file.deliver_date <= limit_date:
        score = score + 3
    if file.file_raw and len(file.file_raw) > 10:
        score = score + 7
    # if file:
    #     reg_ex = b"(select(\s|\t|\n)+\w+)"
    #     match_obj = re.findall(reg_ex, file, re.M | re.I)
    #     points = 0
    #     if match_obj:
    #         inserts = len(match_obj)
    #         score = score + (7 * min(inserts / 15, 1))
    return score


def score_practice_7_lbd(practice_name: str, file: PracticeFile) -> int:
    score = 0
    if not file or exceds_end_date(file.deliver_date):
        return 0
    start_date = datetime(2019, 3, 23, 00, 00)
    limit_date = datetime(2019, 4, 13, 23, 59)
    if start_date <= file.deliver_date <= limit_date:
        score = score + 3
    if file.file_raw and len(file.file_raw) > 10:
        score = score + 7
    # if file:
    #     reg_ex = b"(create(\s|\t|\n)+view(\s|\t|\n)+(\[?\w+\]?\.?)+)"
    #     match_obj = re.findall(reg_ex, file, re.M | re.I)
    #     points = 0
    #     if match_obj:
    #         inserts = len(match_obj)
    #         score = score + (7 * min(inserts / 5, 1))
    return score


def score_practice_8_lbd(practice_name: str, file: PracticeFile) -> int:
    score = 0
    if not file or exceds_end_date(file.deliver_date):
        return 0
    start_date = datetime(2019, 3, 30, 00, 00)
    limit_date = datetime(2019, 4, 20, 23, 59)
    if start_date <= file.deliver_date <= limit_date:
        score = score + 3
    if file.file_raw and len(file.file_raw) > 10:
        score = score + 7
    # if file:
    #     reg_ex = b"(create(\s|\t|\n)+trigger(\s|\t|\n)+(\[?\w+\]?\.?)+)"
    #     match_obj = re.findall(reg_ex, file, re.M | re.I)
    #     points = 0
    #     if match_obj:
    #         inserts = len(match_obj)
    #         score = score + (2 * min(inserts / 1, 1))
    #     reg_ex = b"(create(\s|\t|\n)+(stored(\s|\t|\n)+)?procedure(\s|\t|\n)+(\[?\w+\]?\.?)+)"
    #     match_obj = re.findall(reg_ex, file, re.M | re.I)
    #     points = 0
    #     if match_obj:
    #         inserts = len(match_obj)
    #         score = score + (3 * min(inserts / 5, 1))
    #     reg_ex = b"(create(\s|\t|\n)+function(\s|\t|\n)+(\[?\w+\]?\.?)+)"
    #     match_obj = re.findall(reg_ex, file, re.M | re.I)
    #     points = 0
    #     if match_obj:
    #         inserts = len(match_obj)
    #         score = score + (2 * min(inserts / 1, 1))
    return score


def exceds_end_date(delivery_date: datetime):
    end_date = datetime(2019, 4, 28, 23, 59)
    return delivery_date > end_date


def score_pia_lbd(practice_name: str, file: PracticeFile) -> int:
    score = 0
    end_date = datetime(2019, 5, 6, 00, 00)
    if not file or file.deliver_date < end_date:
        return 0
    start_date = datetime(2019, 3, 30, 00, 00)
    limit_date = datetime(2019, 4, 20, 23, 59)
    if start_date <= file.deliver_date <= limit_date:
        score = score + 3
    if file.file_raw and len(file.file_raw) > 10:
        score = score + 7
    return score * 2


def score_practice_lbd(end_date: datetime, start_date: datetime, limit_date: datetime,
                       score_file: Callable[[str, PracticeFile], int], practice_name: str,
                       file: PracticeFile) -> int:
    score = 0
    if not file or file.deliver_date > end_date:
        return score
    if start_date <= file.deliver_date <= limit_date:
        score = score + 3
    if file and len(file.file_info) > 0:
        score = score + score_file(practice_name, file)
    return score


lbd_min_review = partial(score_practice_lbd, end_date=datetime(2019, 4, 28, 23, 59),
                         score_file=(lambda x, y: 7))

lbd_2nd_review = partial(score_practice_lbd, end_date=datetime(2019, 6, 9, 23, 59),
                         score_file=(lambda x, y: 7), start_date=datetime(2019, 2, 9, 00, 00),
                         limit_date=datetime(2019, 6, 9, 23, 59))

lbd_2nd_PIA_review = partial(score_practice_lbd, end_date=datetime(2019, 6, 9, 23, 59),
                         score_file=(lambda x, y: 17), start_date=datetime(2019, 2, 9, 00, 00),
                         limit_date=datetime(2019, 6, 9, 23, 59))

lbd_p1 = Practice("Practica1", [p1_re], False, lbd_2nd_review,
                  )
lbd_p2 = Practice("Practica2", [p2_re], False, lbd_2nd_review)
lbd_p3 = Practice("Practica3", [p3_re], False, lbd_2nd_review)
lbd_p4 = Practice("Practica4", [p4_re], False, lbd_2nd_review)
lbd_p5 = Practice("Practica5", [p5_re], False, lbd_2nd_review)
lbd_p6 = Practice("Practica6", [p6_re], False, lbd_2nd_review)
lbd_p7 = Practice("Practica7", [p7_re], False, lbd_2nd_review)
lbd_p8 = Practice("Practica8", [p8_re], False, lbd_2nd_review)
lbd_pia = Practice("PIA", [pia_re], False, lbd_2nd_review)
