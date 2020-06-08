import json
from typing import Dict, List, Callable
from unittest import TestCase

from pandas import Series, DataFrame

from src.reviewer.PracticeReviewer import review_practice_from_df, check_and_review_practice
from src.reviewer.git_retrivers import rx_review_practice_from_df, get_querier, \
    check_and_review_practice_from_git, review_practice_from_df_from_git
from src.reviewer.github_request_client import github_get_commit_list_of_a_file, github_get_file_info, github_get_file
from src.reviewer.scores.LBD_Practice_Scores import lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, \
    lbd_pia
from src.reviewer.scores.LDOOPracticeScores import ldoo_p1, ldoo_p2, ldoo_p3, ldoo_p4, ldoo_p5, ldoo_p6, ldoo_p7, ldoo_p8, \
    ldoo_p9, ldoo_p10
from src.utils.my_pandas_util import parse_csv_df
from src.utils.url import get_response_content


def get_querier_with_credentials():
    with open('./resources/my_data.json') as f:
        my_data = json.load(f)
    return get_querier(my_data["client_id"], my_data["client_secret"])


fake_file_info_map = {'tarea1': {},  # path : List of files in path
                 'tarea2': {},
                 'tarea3': {},
                 '': [{'name': 'PIAFINAL.sql', 'type': 'file', 'path': 'PIAFINAL.sql',
                       'download_url': 'mock.url/PIAFINAL.SQL'}]}
file_commit_map = {'tarea1': [{}],
                   'tarea2': [{}],
                   'PIAFINAL.sql': [{}, {'commit': {'committer': {'date': '2019-06-05T04:00:00Z'}}}],
                   }
file_content_map = {'mock.url/PIAFINAL.SQL': b'Contenido del tarea'
                    }


def get_mock_file_info_fn(file_info_dict: Dict, default: Dict = dict()) -> Callable[[str, str, str, str], Dict]:
    def get_mock_file_info(site: str, repo: str, user: str, filepath: str) -> Dict:
        return file_info_dict.get(filepath, default)
    return get_mock_file_info


def get_mock_commit_list_of_a_file_fn(file_commit_dict: Dict, default: List[Dict] = [{}]) \
    -> Callable[[str, str, str, str], List[Dict]]:
    def get_mock_commit_list_of_a_file(site: str, repo: str, user: str, filepath: str) -> List[Dict]:
        return file_commit_dict.get(filepath, default)
    return get_mock_commit_list_of_a_file


def get_mock_file_content_fn(file_content_dict: Dict[str, bytes], default: bytes = b'') \
    -> Callable[[str], bytes]:
    def get_mock_file_content(path: str) -> bytes:
        return file_content_dict.get(path, default)
    return get_mock_file_content


class TestTest(TestCase):
    def test_get_file(self):
        querier = get_querier_with_credentials()
        file = querier(github_get_file)("github.com", "ppgodel", "SchoolReview",
                                        "test/resources/practicas_ldoo.csv")
        assert file

    def test_review_group_ldb(self):
        querier = get_querier_with_credentials()
        df_lbd = parse_csv_df("./resources/LBD_repos.csv")
        p1 = review_practice_from_df_from_git(df_lbd, querier(github_get_file_info),
                                              querier(github_get_commit_list_of_a_file),
                                              get_response_content,
                                              lbd_pia)
        df_lbd[lbd_p1.name] = p1
        # df_lbd.to_csv("test/resources/LBD_repos.csv")

    def test_review_group_lbd_rx(self):
        def get_dict_to_test() -> DataFrame:
            return DataFrame([
                {'Matricula': '1',
                 'Nombre': 'foo',
                 'Primer apellido': 'Last1',
                 'Segundo apellido': 'Last2',
                 'Grupo': 'LBD',
                 'repo_site': 'github.com',
                 'repo_user': 'foo',
                 'repo_name': 'LBD',
                 'Practica1': None},
                {'Matricula': '2',
                 'Nombre': 'bar',
                 'Primer apellido': 'Last1',
                 'Segundo apellido': 'Last2',
                 'Grupo': 'LBD',
                 'repo_site': 'github.com',
                 'repo_user': 'bar',
                 'repo_name': 'LBD',
                 'Practica1': None},
                {'Matricula': '3',
                 'Nombre': 'baz',
                 'Primer apellido': 'Last1',
                 'Segundo apellido': 'Last2',
                 'Grupo': 'LBD',
                 'repo_site': 'github.com',
                 'repo_user': 'baz',
                 'repo_name': 'LBD',
                 'Practica1': None},
            ])

        df_lbd = get_dict_to_test()
        obs = rx_review_practice_from_df(df_lbd, get_mock_file_info_fn(fake_file_info_map),
                                         get_mock_commit_list_of_a_file_fn(file_commit_map),
                                         get_mock_file_content_fn(file_content_map),
                                         lbd_pia)
        l = []
        obs.subscribe(lambda x: l.append(x))
        print(l)
        self.assertTrue(l)
        # self.assertTrue(l[0]['PIA'].equals(Series(data=[10, 10, 10], name='PIA')))
    def test_review_ldb(self):
        querier = get_querier_with_credentials()
        # student_row = Series(
        #     {"Matricula": "1941554", "repo_site": "github.com", "repo_user": "RogueWhite",
        #      "repo_name": "LBD"})
        student_row = Series(data=["1941554","github.com", "RogueWhite", "LBD"],
                             index=["Matricula", "repo_site", "repo_user", "repo_name"])
        practices = [lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, lbd_pia]

        for practice in practices:
            check_and_review_practice_from_row = check_and_review_practice_from_git(
                querier(github_get_file_info), querier(github_get_commit_list_of_a_file),
                get_response_content, practice)
            calif = check_and_review_practice_from_row(student_row)
            print("{}: {}".format(practice.name, calif))

    def test_review_pia_ldb(self):
        querier = get_querier_with_credentials()
        # student_row = Series(
        #     {"Matricula": "1941554", "repo_site": "github.com", "repo_user": "RogueWhite",
        #      "repo_name": "LBD"}),
        student_row = Series(data=["1941554", "github.com", "RogueWhite", "LBD"],
                             index=["Matricula", "repo_site", "repo_user", "repo_name"])

        check_and_review_practice_from_row = check_and_review_practice_from_git(
            querier(github_get_file_info), querier(github_get_commit_list_of_a_file),
            get_response_content, lbd_pia)

        calif = check_and_review_practice_from_row(student_row)
        print(calif)

    # def test_review_ldoo(self):
    #     querier = get_querier_with_credentials()
    #     student_row = Series(
    #         {"Matricula": "1671623", "repo_site": "github.com", "repo_user": "GerardoOchoa229",
    #          "repo_name": "LDOO_1851232"})
    #     practices = [ldoo_p1, ldoo_p2, ldoo_p3, ldoo_p4, ldoo_p5, ldoo_p6, ldoo_p7, ldoo_p8, ldoo_p9, ldoo_p10]

        # for practice in practices:
        #     calif = check_and_review_practice(practice)
        #     print(calif)
    #
    # def test_review_pia_ldoo(self):
    #     querier = get_querier_with_credentials()
    #     student_row = Series(
    #         {"Matricula": "1669068", "repo_site": "github.com", "repo_user": "guillermo-fcfm",
    #          "repo_name": "Lab-BD"})
    #
    #     calif = check_and_review_practice(querier(github_get_file_info),
    #                                       querier(github_get_commit_list_of_a_file),
    #                                       student_row, lbd_pia)
    #     print(calif)
