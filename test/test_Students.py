from unittest import TestCase

from src.Students import get_querier, build_student, github_get_repository_list_by, build_course_from_csv
import json

LDOO = 'LDOO'
LBD = 'LBD'


def get_querier_with_credentials():
    with open('test/resources/my_data.json') as f:
        my_data = json.load(f)
    return get_querier(my_data["client_id"], my_data["client_secret"])


class TestAlumno(TestCase):
    def test_get_alumno(self):
        querier = get_querier_with_credentials()
        a = build_student(querier(github_get_repository_list_by), "1186622", LDOO, "github.com")
        self.assertIsNone(a)
        a = build_student(querier(github_get_repository_list_by), "1186622", LDOO, "http://github.com/")
        self.assertIsNone(a)
        a = build_student(querier(github_get_repository_list_by), "1186622", LDOO,
                          "http://www.github.com/ppgodel/LDOO_EJ_19")
        self.assertIsNotNone(a)
        a = build_student(querier(github_get_repository_list_by), "1186622", LDOO, "github.com/ppgodel/LDOO_EJ_19")
        self.assertIsNotNone(a)
        a = build_student(querier(github_get_repository_list_by), "1186622", LDOO, "github.com/ppgodel/")
        self.assertEqual("LDOO_EJ_19", a.git_repo)
        a = build_student(querier(github_get_repository_list_by), "1186622", LDOO, "github.com/ppgodel/lol")
        self.assertEqual("LDOO_EJ_19", a.git_repo)

    def test_from_file_ldoo(self):
        querier = get_querier_with_credentials()
        # columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido", "Grupo"]
        base_columns = ["Matricula", "Nombre(s)", "Primer Apellido", "Segundo Apellido", "Grupo"]
        new_columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido", "Grupo"]
        a = build_course_from_csv(querier(github_get_repository_list_by),
                                  "test/resources/students_ldoo.csv", ' direccion de tu repositorio GIT',
                                  base_columns, new_columns)
        a.to_csv('test/resources/LDOO_repos.csv', sep=',', encoding='utf-8', index=False)
        self.assertIsNotNone(a)
        # import pandas


    def test_from_file_lbd(self):
        querier = get_querier_with_credentials()
        base_columns = ["Matricula", "Nombres", "Apellido Paterno", "Apellido Materno", "Laboratorio a cursar"]
        new_columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido", "Grupo"]
        a = build_course_from_csv(querier(github_get_repository_list_by),
                                  "test/resources/practicas_lbd.csv", 'Repositorio',
                                  base_columns, new_columns)
        a.to_csv('test/resources/LBD_repos.csv', sep=',', encoding='utf-8', index=False)
        self.assertIsNotNone(a)