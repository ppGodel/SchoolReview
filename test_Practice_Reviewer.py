import json
from unittest import TestCase

from PracticeReviewer import parse_csv_df, review_practice_from_df, lbd_p1
from Students import get_querier, github_get_file, github_get_commit_list_of_a_file, github_get_file_info


def get_querier_with_credentials():
    with open('test/resources/my_data.json') as f:
        my_data = json.load(f)
    return get_querier(my_data["client_id"], my_data["client_secret"])


class TestTest(TestCase):

    def test_get_file(self):
        querier = get_querier_with_credentials()
        file = querier(github_get_file)("github.com", "ppgodel", "SchoolReview", "test/resources/practicas_ldoo.csv")
        assert file

    def test_review_ldb(self):
        querier = get_querier_with_credentials()
        df_lbd = parse_csv_df("test/resources/LBD_repos.csv")
        p1 = review_practice_from_df(df_lbd, querier(github_get_file_info), querier(github_get_commit_list_of_a_file),
                                     lbd_p1)
        df_lbd[lbd_p1.name] = p1
        df_lbd.to_csv("test/resources/LBD_repos.csv")
