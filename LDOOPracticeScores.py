import datetime
from datetime import datetime

from PracticeReviewer import Practice
from practice_re import p1_re


def exceds_end_date(delivery_date: datetime):
    end_date = datetime(2019, 4, 28, 23, 59)
    return True if delivery_date > end_date else False


def score_practice_1_ldoo(practice_name: str, delivery_date: datetime, file: bytes) -> int:
    score = 0
    if exceds_end_date(delivery_date):
        return 0
    start_date = datetime(2019, 2, 2, 00, 00)
    limit_date = datetime(2019, 3, 2, 23, 59)
    if start_date <= delivery_date <= limit_date:
        score = score + 3
    if file and len(file) > 10:
        score = score + 7
    return score


ldoo_p1 = Practice("Practica1", [p1_re],
                  True, score_practice_1_ldoo)
