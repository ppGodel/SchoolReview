import json
from typing import Dict, List
from unittest import TestCase

from pandas import Series, DataFrame

from reviewer.PracticeReviewer import review_practice_from_df, check_and_review_practice
from reviewer.git_retrivers import rx_review_practice_from_df, get_querier
from reviewer.github_request_client import github_get_commit_list_of_a_file, github_get_file_info, github_get_file
from reviewer.scores.LBD_Practice_Scores import lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, \
    lbd_pia
from reviewer.scores.LDOOPracticeScores import ldoo_p1, ldoo_p2, ldoo_p3, ldoo_p4, ldoo_p5, ldoo_p6, ldoo_p7, ldoo_p8, \
    ldoo_p9, ldoo_p10
from utils.pandas import parse_csv_df


def get_querier_with_credentials():
    with open('test/resources/my_data.json') as f:
        my_data = json.load(f)
    return get_querier(my_data["client_id"], my_data["client_secret"])


file_info_map = {'tarea1': {},  # path : List of files in path
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


def get_mock_file_info(site: str, repo: str, user: str, filepath: str) -> Dict:
    return file_info_map.get(filepath, {})


def get_mock_commit_list_of_a_file(site: str, repo: str, user: str, filepath: str) -> List[Dict]:
    return file_commit_map.get(filepath, [{}])


def get_mock_file_content(path: str) -> bytes:
    return file_content_map[path]


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
        obs = rx_review_practice_from_df(df_lbd, get_mock_file_info,
                                         get_mock_commit_list_of_a_file,
                                         get_mock_file_content,
                                         lbd_pia)
        l = []
        obs.subscribe(lambda x: l.append(x))
        self.assertTrue(l[0]['PIA'].equals(Series(data=[10, 10, 10], name='PIA')))
        # df_lbd[lbd_p1.name] = p1
        # df_lbd.to_csv("test/resources/LBD_repos.csv")


    def test_review_ldb(self):
        querier = get_querier_with_credentials()
        student_row = Series(
            {"Matricula": "1752659", "repo_site": "github.com", "repo_user": "AlonsoBarrientosLSTI",
             "repo_name": "LBD-"})
        practices = [lbd_p1, lbd_p2, lbd_p3, lbd_p4, lbd_p5, lbd_p6, lbd_p7, lbd_p8, lbd_pia]

        for practice in practices:
            calif = check_and_review_practice(querier(github_get_file_info),
                                              querier(github_get_commit_list_of_a_file),
                                              student_row, practice)
            print("{}: {}".format( practice.name,calif))

    def test_review_pia_ldb(self):
        querier = get_querier_with_credentials()
        student_row = Series(
            {"Matricula": "1752659", "repo_site": "github.com", "repo_user": "AlonsoBarrientosLSTI",
             "repo_name": "LBD-"})

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
