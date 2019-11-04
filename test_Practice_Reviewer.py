import json
from unittest import TestCase

from pandas import Series

from src.reviewer.PracticeReviewer import review_practice_from_df, check_and_review_practice, rx_review_practice_from_df
from src.utils.pandas import parse_csv_df
from LBD_Practice_Scores import lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, \
    lbd_pia
from LDOOPracticeScores import ldoo_p1, ldoo_p2, ldoo_p3, ldoo_p4, ldoo_p5, ldoo_p6, ldoo_p7, ldoo_p8, ldoo_p9, ldoo_p10
from Students import get_querier, github_get_file, github_get_commit_list_of_a_file, \
    github_get_file_info


def get_querier_with_credentials():
    with open('test/resources/my_data.json') as f:
        my_data = json.load(f)
    return get_querier(my_data["client_id"], my_data["client_secret"])


class TestTest(TestCase):

    def test_get_file(self):
        querier = get_querier_with_credentials()
        file = querier(github_get_file)("github.com", "ppgodel", "SchoolReview",
                                        "test/resources/practicas_ldoo.csv")
        assert file

    def test_review_group_ldb(self):
        querier = get_querier_with_credentials()
        df_lbd = parse_csv_df("test/resources/LBD_repos.csv")
        p1 = review_practice_from_df(df_lbd, querier(github_get_file_info),
                                     querier(github_get_commit_list_of_a_file),
                                     lbd_pia)
        df_lbd[lbd_p1.name] = p1
        df_lbd.to_csv("test/resources/LBD_repos.csv")

    def test_review_group_lbd_rx(self):
        querier = get_querier_with_credentials()
        df_lbd = parse_csv_df("test/resources/LBD_repos.csv")
        rx_review_practice_from_df(df_lbd, querier(github_get_file_info),
                                     querier(github_get_commit_list_of_a_file),
                                     lbd_pia, (lambda x: df_lbd[lbd_p1.name] ))
        # df_lbd[lbd_p1.name] = p1
        df_lbd.to_csv("test/resources/LBD_repos.csv")


    def test_review_ldb(self):
        querier = get_querier_with_credentials()
        student_row = Series(
            {"Matricula": "1669068", "repo_site": "github.com", "repo_user": "IvanRuiz11",
             "repo_name": "Lab-Base-de-Datos"})
        practices = [lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, lbd_pia]

        for practice in practices:
            calif = check_and_review_practice(querier(github_get_file_info),
                                              querier(github_get_commit_list_of_a_file),
                                              student_row, practice)
            print(calif)

    def test_review_pia_ldb(self):
        querier = get_querier_with_credentials()
        student_row = Series(
            {"Matricula": "1669068", "repo_site": "github.com", "repo_user": "guillermo-fcfm",
             "repo_name": "Lab-BD"})

        calif = check_and_review_practice(querier(github_get_file_info),
                                          querier(github_get_commit_list_of_a_file),
                                          student_row, lbd_pia)
        print(calif)

    def test_review_ldoo(self):
        querier = get_querier_with_credentials()
        student_row = Series(
            {"Matricula": "1671623", "repo_site": "github.com", "repo_user": "GerardoOchoa229",
             "repo_name": "LDOO_1851232"})
        practices = [ldoo_p1, ldoo_p2, ldoo_p3, ldoo_p4, ldoo_p5, ldoo_p6, ldoo_p7, ldoo_p8, ldoo_p9, ldoo_p10]

        for practice in practices:
            calif = check_and_review_practice(querier(github_get_file_info),
                                          querier(github_get_commit_list_of_a_file),
                                          student_row, practice)
            print(calif)

    def test_review_pia_ldoo(self):
        querier = get_querier_with_credentials()
        student_row = Series(
            {"Matricula": "1669068", "repo_site": "github.com", "repo_user": "guillermo-fcfm",
             "repo_name": "Lab-BD"})

        calif = check_and_review_practice(querier(github_get_file_info),
                                          querier(github_get_commit_list_of_a_file),
                                          student_row, lbd_pia)
        print(calif)
