#!/usr/bin/env python
from datetime import datetime, timedelta
from typing import Callable

from src.reviewer.PracticeReviewer import Practice, PracticeFile, Course
from src.reviewer.scores.practice_re import p1_re, p2_re, p3_re, p4_re, p5e_re, \
    p6e_re, p7_re, p8_re, p9e_re, p10_re, p11_re, p12_re, p13_re, p14_re
from functools import partial


def score_min_practice_lpe(end_date: datetime, start_date: datetime, limit_date: datetime,
                            score_file: Callable[[str, PracticeFile], int], practice_name: str, file: PracticeFile) -> int:
    score = 0
    if not file or file.deliver_date > end_date:
        return score
    if file and len(file.file_info) > 0:
        score = score + score_file(practice_name, file)
    return score


lpe_min_review = partial(score_min_practice_lpe, end_date=datetime(2020, 6, 9, 23, 59))

first_class = datetime(2020, 1, 15, 0, 0)
last_class = datetime(2020, 6, 6, 0, 0)
one_week = timedelta(days=7)
two_weeks = timedelta(days=15)
lpe_p1 = Practice("Practica1", [p1_re], [p1_re], True, partial(lpe_min_review,
                                                               score_file=(lambda x, y: 3),
                                                               start_date=first_class,
                                                               limit_date=last_class))
second_class = first_class + one_week
lpe_p2 = Practice("Practica2", [p2_re], [p2_re], True, partial(lpe_min_review,
                                                               score_file=(lambda x, y: 3),
                                                               start_date=first_class,
                                                               limit_date=last_class))
third_class = second_class + one_week
lpe_p3 = Practice("Practica3", [p3_re], [p3_re], True, partial(lpe_min_review,
                                                               score_file=(lambda x, y: 5),
                                                               start_date=first_class,
                                                               limit_date=last_class))
fourth_class = third_class + one_week
lpe_p4 = Practice("Practica4", [p4_re], [p4_re], True, partial(lpe_min_review,
                                                               score_file=(lambda x, y: 5),
                                                               start_date=first_class,
                                                               limit_date=last_class))
fifth_class = fourth_class + one_week
lpe_p5 = Practice("Practica5", [p5e_re], [p5e_re], True, partial(lpe_min_review,
                                                                 score_file=(lambda x, y: 5),
                                                                 start_date=first_class,
                                                                 limit_date=last_class))
sixth_class = fifth_class + one_week
lpe_p6 = Practice("Practica6", [p6e_re], [p6e_re], True, partial(lpe_min_review,
                                                                 score_file=(lambda x, y: 7),
                                                                 start_date=first_class,
                                                                 limit_date=last_class))
seventh_class = sixth_class + one_week
lpe_p7 = Practice("Practica7", [p7_re], [p7_re], True, partial(lpe_min_review,
                                                               score_file=(lambda x, y: 9),
                                                               start_date=first_class,
                                                               limit_date=last_class))
eighth_class = seventh_class + one_week
lpe_p8 = Practice("Practica8", [p8_re], [p8_re], True, partial(lpe_min_review,
                                                               score_file=(lambda x, y: 9),
                                                               start_date=first_class,
                                                               limit_date=last_class))
ninth_class = eighth_class + one_week
lpe_p9 = Practice("Practica9", [p9e_re], [p9e_re], True, partial(lpe_min_review,
                                                                 score_file=(lambda x, y: 8),
                                                                 start_date=first_class,
                                                                 limit_date=last_class))
tenth_class = ninth_class + one_week
lpe_p10 = Practice("Practica10", [p10_re], [p10_re], True, partial(lpe_min_review,
                                                                   score_file=(lambda x, y: 12),
                                                                   start_date=first_class,
                                                                   limit_date=last_class))

lpe_p11 = Practice("Practica11", [p11_re], [p11_re], True, partial(lpe_min_review,
                                                                   score_file=(lambda x, y: 12),
                                                                   start_date=first_class,
                                                                   limit_date=last_class))

lpe_p12 = Practice("Practica12", [p12_re], [p12_re], True, partial(lpe_min_review,
                                                                   score_file=(lambda x, y: 6),
                                                                   start_date=first_class,
                                                                   limit_date=last_class))


lpe_p13 = Practice("Practica13", [p12_re, p13_re], [p12_re, p13_re], True, partial(lpe_min_review,
                                                                   score_file=(lambda x, y: 6),
                                                                   start_date=first_class,
                                                                   limit_date=last_class))


lpe_p14 = Practice("Practica14", [p13_re, p14_re], [p13_re, p14_re], True, partial(lpe_min_review,
                                                                   score_file=(lambda x, y: 10),
                                                                   start_date=first_class,
                                                                   limit_date=last_class))

