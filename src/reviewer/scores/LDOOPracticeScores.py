import datetime
from datetime import datetime
from typing import Callable

from src.reviewer.PracticeReviewer import Practice, PracticeFile
from src.reviewer.scores.practice_re import *
from functools import partial


def exceds_end_date(delivery_date: datetime):
    end_date = datetime(2019, 4, 28, 23, 59)
    return True if delivery_date > end_date else False


def score_practice_1_ldoo(end_date: datetime, start_date: datetime, limit_date: datetime,
                          score_file: Callable[[str, PracticeFile], int], practice_name: str, file: PracticeFile) -> int:
    score = 0
    if not file or file.deliver_date > end_date:
        return score
    if start_date <= file.deliver_date <= limit_date:
        score = score + 3
    if file and len(file.file_info) > 0:
        score = score + score_file(practice_name, file)
    return score


ldoo_min_review = partial(score_practice_1_ldoo, end_date=datetime(2019, 6, 6, 23, 59), score_file=(lambda x, y: 7))

ldoo_p1 = Practice("Practica1", [p1_re], True, partial(ldoo_min_review,
                                                       start_date=datetime(2019, 2, 2, 00, 00),
                                                       limit_date=datetime(2019, 3, 2, 23, 59)))
ldoo_p2 = Practice("Practica2", [p2_re], True, partial(ldoo_min_review,
                                                        start_date=datetime(2019, 2, 9, 00, 00),
                                                        limit_date=datetime(2019, 3, 2, 23, 59)))
ldoo_p3 = Practice("Practica3", [p3_re], True, partial(ldoo_min_review,
                                                        start_date=datetime(2019, 2, 16, 00, 00),
                                                        limit_date=datetime(2019, 3, 9, 23, 59)))
ldoo_p4 = Practice("Practica4", [p4_re], True, partial(ldoo_min_review,
                                                        start_date=datetime(2019, 2, 25, 00, 00),
                                                        limit_date=datetime(2019, 3, 16, 23, 59)))
ldoo_p5 = Practice("Practica5", [p5e_re], True, partial(ldoo_min_review,
                                                        start_date=datetime(2019, 3, 2, 00, 00),
                                                        limit_date=datetime(2019, 3, 23, 23, 59)))
ldoo_p6 = Practice("Practica6", [p6e_re], True, partial(ldoo_min_review,
                                                        start_date=datetime(2019, 3, 9, 00, 00),
                                                        limit_date=datetime(2019, 3, 30, 23, 59)))
ldoo_p7 = Practice("Practica7", [p7_re], True, partial(ldoo_min_review,
                                                        start_date=datetime(2019, 3, 16, 00, 00),
                                                        limit_date=datetime(2019, 4, 6, 23, 59)))
ldoo_p8 = Practice("Practica8", [p8_re], True, partial(ldoo_min_review,
                                                        start_date=datetime(2019, 3, 23, 00, 00),
                                                        limit_date=datetime(2019, 4, 13, 23, 59)))
ldoo_p9 = Practice("Practica9", [p9e_re], True, partial(ldoo_min_review,
                                                        start_date=datetime(2019, 3, 30, 00, 00),
                                                        limit_date=datetime(2019, 4, 20, 23, 59)))
ldoo_p10 = Practice("Practica10", [p10e_re], True, partial(ldoo_min_review,
                                                          start_date=datetime(2019, 4, 4, 00, 00),
                                                          limit_date=datetime(2019, 3, 2, 23, 59)))
