from unittest import TestCase
from oldway.GitChecker import *


class TestPracticeChecker(TestCase):

    def assert_formatter(self, repo, expected):
        returned_value = repository_formatter(repo)
        print(str(expected) + ":" + str(returned_value))
        self.assertEqual(expected, returned_value)

    def test_repository_formatter(self):
        self.assert_formatter(None, [])
        self.assert_formatter("", [])
        self.assert_formatter("github.com/ppgodel/LDOO_EJ_19", ["https://github.com/ppgodel/LDOO_EJ_19"])
        self.assert_formatter("github.com/ppgodel",
                              ["https://github.com/ppgodel/LDOO_EJ_19", "https://github.com/ppgodel/LDOO",
                               "https://github.com/ppgodel/LDOO_EJ_2019",
                               "https://github.com/ppgodel/LDOO_Enero_Julio_19",
                               "https://github.com/ppgodel/LDOO_Enero_Julio_2019"])

    def test_repository_check(self):
        self.assertFalse(repository_check(None))
        self.assertFalse(repository_check(""))
        self.assertFalse(repository_check("github.com"))
        self.assertFalse(repository_check("github.com/ppgodel"))
        self.assertFalse(repository_check("https://github.com/ppGodel/Wrong"))
        self.assertTrue(repository_check("https://github.com/ppGodel/LDOO_EJ_19"))

    def test_get_pn(self):
        self.assertTrue(check_equal(generate_practice_name_list_from_local(1),
                                    ["Practica1", "P1", "Tarea1", "Ejercicio1", "P1", "Practica01",
                                     "P01", "Tarea01", "Ejercicio01", "P01"]))
        self.assertTrue(check_equal(generate_practice_name_list_from_local(10), ["Practica10", "P10", "Tarea10", "Ejercicio10", "P10"]))

    def test_url_check(self):
        def assert_check_repository(expected, value):
            returned_value = get_repository(value)
            print(expected + " : " + returned_value)
            self.assertEqual(returned_value, expected)

        assert_check_repository("", None)
        assert_check_repository("", "")
        assert_check_repository("", "github.com")
        assert_check_repository("", "github.com")
        assert_check_repository("https://github.com/ppgodel/LDOO_EJ_19", "github.com/ppgodel/LDOO_EJ_19")
        assert_check_repository("https://github.com/ppgodel/LDOO_EJ_19", "github.com/ppgodel")

    def test_practice_checker(self):
        def assert_practice_checker(expected, value, practice):
            returned_value = practice_checker(value, practice)
            print(str(expected) + " : " + str(returned_value))
            self.assertEqual(returned_value, expected)

        assert_practice_checker(False, "", 1)
        assert_practice_checker(False, None, 1)
        assert_practice_checker(False, "github.com", 1)
        assert_practice_checker(True, "github.com/ppgodel", 1)
        assert_practice_checker(True, "github.com/ppgodel/LDOO_EJ_19", 1)
