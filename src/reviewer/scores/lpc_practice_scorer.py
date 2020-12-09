#!/usr/bin/env python3
from functools import partial
from datetime import datetime, timedelta
from typing import Callable
from src.reviewer.PracticeReviewer import Practice, PracticeFile, Course
from src.reviewer.scores.practice_re import p1_re, p2_re, p3_re, p4_re, p5e_re, \
    p6e_re, p7_re, p8_re, p9e_re, p10_re, p11_re, p12_re


def score_min_practice_lpc(end_date: datetime, start_date: datetime, limit_date: datetime,
                           score_file: Callable[[str, PracticeFile], int], practice_name: str, practice_file: PracticeFile) -> int:
    score = 0
    print("s {}, d {}, l {}, e {}".format( start_date, practice_file.deliver_date, limit_date, end_date))
    if practice_file:
        if  start_date < practice_file.deliver_date < limit_date:
            score += 3
        if practice_file.deliver_date < end_date and len(practice_file.file_info) > 0:
            score += score_file(practice_name, practice_file)
    return score


lpc_min_review = partial(score_min_practice_lpc, end_date=datetime(2020, 12, 4, 23, 59))

first_class = datetime(2020, 9, 19, 0, 0)
last_class = datetime(2020, 12, 5, 0, 0)
one_week = timedelta(days=7)
two_weeks = timedelta(days=15)
three_weeks = timedelta(days=22)
lpc_p1 = Practice("Practica1", [p1_re], [p1_re], True, partial(lpc_min_review,
                                                               score_file=(lambda x, y: 7),
                                                               start_date=first_class,
                                                               limit_date=first_class + three_weeks))
second_class = first_class + one_week
lpc_p2 = Practice("Practica2", [p2_re], [p2_re], True, partial(lpc_min_review,
                                                               score_file=(lambda x, y: 7),
                                                               start_date=second_class,
                                                               limit_date=second_class + three_weeks))
third_class = second_class + one_week
lpc_p3 = Practice("Practica3", [p3_re], [p3_re], True, partial(lpc_min_review,
                                                               score_file=(lambda x, y: 7),
                                                               start_date=third_class,
                                                               limit_date=third_class + three_weeks))
fourth_class = second_class + one_week
lpc_p4 = Practice("Practica4", [p4_re], [p4_re], True, partial(lpc_min_review,
                                                               score_file=(lambda x, y: 7),
                                                               start_date=fourth_class,
                                                               limit_date=fourth_class + three_weeks))
fifth_class = fourth_class + one_week
lpc_p5 = Practice("Practica5", [p5e_re], [p5e_re], True, partial(lpc_min_review,
                                                                 score_file=(lambda x, y: 7),
                                                                 start_date=fifth_class,
                                                                 limit_date=fifth_class + three_weeks))
sixth_class = fifth_class + one_week
lpc_p6 = Practice("Practica6", [p6e_re], [p6e_re], True, partial(lpc_min_review,
                                                                 score_file=(lambda x, y: 7),
                                                                 start_date=sixth_class,
                                                                 limit_date=sixth_class + three_weeks))
seventh_class = sixth_class + one_week
lpc_p7 = Practice("Practica7", [p7_re], [p7_re], True, partial(lpc_min_review,
                                                               score_file=(lambda x, y: 7),
                                                               start_date=seventh_class,
                                                               limit_date=seventh_class + three_weeks))
eighth_class = sixth_class + one_week
lpc_p8 = Practice("Practica8", [p8_re], [p8_re], True, partial(lpc_min_review,
                                                               score_file=(lambda x, y: 7),
                                                               start_date=eighth_class,
                                                               limit_date=eighth_class + three_weeks))
ninth_class = eighth_class + one_week
lpc_p9 = Practice("Practica9", [p9e_re], [p9e_re], True, partial(lpc_min_review,
                                                                 score_file=(lambda x, y: 7),
                                                                 start_date=ninth_class,
                                                                 limit_date=ninth_class + three_weeks))
tenth_class = ninth_class + one_week
lpc_p10 = Practice("Practica10", [p10_re], [p10_re], True, partial(lpc_min_review,
                                                                   score_file=(lambda x, y: 7),
                                                                   start_date=tenth_class,
                                                                   limit_date=tenth_class + three_weeks))

eleventh_class = tenth_class + one_week
lpc_p11 = Practice("Practica11", [p11_re, p12_re], [p11_re, p12_re], True, partial(lpc_min_review,
                                                                   score_file=(lambda x, y: 7),
                                                                   start_date=eleventh_class,
                                                                   limit_date=eleventh_class + three_weeks))

