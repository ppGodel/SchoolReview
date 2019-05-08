from unittest import TestCase

from Students import  StudentBuilder, CourseBuilder
import json

LDOO = 'LDOO'
LBD = 'LBD'


class TestAlumno(TestCase):
    def _arrange(self):
        with open('test/resources/my_data.json') as f:
            my_data = json.load(f)
        self.sb = StudentBuilder(my_data["auth_user"], my_data["auth_pass"])
        self.cb = CourseBuilder(self.sb)


    def test_get_alumno(self):
        self._arrange()
        a = self.sb.build_student("1186622", LDOO, "github.com")
        self.assertIsNone(a)
        a = self.sb.build_student("1186622", LDOO, "http://github.com/")
        self.assertIsNone(a)
        a = self.sb.build_student("1186622", LDOO, "http://www.github.com/ppgodel/LDOO_EJ_19")
        self.assertIsNotNone(a)
        a = self.sb.build_student("1186622", LDOO, "github.com/ppgodel/LDOO_EJ_19")
        self.assertIsNotNone(a)
        a = self.sb.build_student("1186622", LDOO, "github.com/ppgodel/")
        self.assertEqual("LDOO_EJ_19", a.repo)
        a = self.sb.build_student("1186622", LDOO, "github.com/ppgodel/lol")
        self.assertEqual("LDOO_EJ_19", a.repo)

    def test_from_file(self):
        self._arrange()
        columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido", "Grupo"]
        a = self.cb.build_course_from_csv("test/resources/students.csv", ' direccion de tu repositorio GIT', columns)
        a.to_csv('test/resources/LDOO_repos.csv', sep=',', encoding='utf-8', index=False)
        self.assertIsNotNone(a)
        #import pandas
