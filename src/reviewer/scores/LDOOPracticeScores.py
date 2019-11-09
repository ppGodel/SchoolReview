import datetime
from datetime import datetime, timedelta
from typing import Callable

from src.reviewer.PracticeReviewer import Practice, PracticeFile
from src.reviewer.scores.practice_re import *
from functools import partial


def score_min_practice_ldoo(end_date: datetime, start_date: datetime, limit_date: datetime,
                            score_file: Callable[[str, PracticeFile], int], practice_name: str, file: PracticeFile) -> int:
    score = 0
    if not file or file.deliver_date > end_date:
        return score
    if start_date <= file.deliver_date <= limit_date:
        score = score + 3
    if file and len(file.file_info) > 0:
        score = score + score_file(practice_name, file)
    return score


ldoo_min_review = partial(score_min_practice_ldoo, end_date=datetime(2019, 11, 9, 23, 59), score_file=(lambda x, y: 7))

first_class = datetime(2019, 8, 23, 0, 0)
one_week = timedelta(days=7)
two_weeks = timedelta(days=15)
ldoo_p1 = Practice("Practica1", [p1_re], True, partial(ldoo_min_review,
                                                       start_date=first_class,
                                                       limit_date=first_class + two_weeks))
second_class = first_class + one_week
ldoo_p2 = Practice("Practica2", [p2_re], True, partial(ldoo_min_review,
                                                       start_date=second_class,
                                                       limit_date=second_class + two_weeks))
third_class = second_class + one_week
ldoo_p3 = Practice("Practica3", [p3_re], True, partial(ldoo_min_review,
                                                       start_date=third_class,
                                                       limit_date=third_class + two_weeks))
fourth_class = third_class + one_week
ldoo_p4 = Practice("Practica4", [p4_re], True, partial(ldoo_min_review,
                                                       start_date=fourth_class,
                                                       limit_date=fourth_class + two_weeks))
fifth_class = fourth_class + one_week
ldoo_p5 = Practice("Practica5", [p5e_re], True, partial(ldoo_min_review,
                                                        start_date=fifth_class,
                                                        limit_date=fifth_class + two_weeks))
sixth_class = fifth_class + one_week
ldoo_p6 = Practice("Practica6", [p6e_re], True, partial(ldoo_min_review,
                                                        start_date=sixth_class,
                                                        limit_date=sixth_class + two_weeks))
seventh_class = sixth_class + one_week
ldoo_p7 = Practice("Practica7", [p7_re], True, partial(ldoo_min_review,
                                                       start_date=seventh_class,
                                                       limit_date=seventh_class + two_weeks))
eighth_class = seventh_class + one_week
ldoo_p8 = Practice("Practica8", [p8_re], True, partial(ldoo_min_review,
                                                        start_date=eighth_class,
                                                        limit_date=eighth_class + two_weeks))
ninth_class = eighth_class + one_week
ldoo_p9 = Practice("Practica9", [p9e_re], True, partial(ldoo_min_review,
                                                        start_date=ninth_class,
                                                        limit_date=ninth_class + two_weeks))
tenth_class = ninth_class + one_week
ldoo_p10 = Practice("Practica10", [p10e_re], True, partial(ldoo_min_review,
                                                          start_date=tenth_class,
                                                          limit_date=tenth_class + two_weeks))

