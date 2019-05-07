from unittest import TestCase

from Students import ClassMate, StudentBuilder, CourseBuilder

LDOO = 'LDOO'
LBD = 'LBD'


class TestAlumno(TestCase):

    def test_get_alumno(self):
        sb = StudentBuilder()
        a = sb.build_student("1186622", LDOO, "github.com")
        self.assertIsNone(a)
        a = sb.build_student("1186622", LDOO, "http://github.com/")
        self.assertIsNone(a)
        a = sb.build_student("1186622", LDOO, "http://www.github.com/ppgodel/LDOO_EJ_19")
        self.assertIsNotNone(a)
        a = sb.build_student("1186622", LDOO, "github.com/ppgodel/LDOO_EJ_19")
        self.assertIsNotNone(a)
        a = sb.build_student("1186622", LDOO, "github.com/ppgodel/")
        self.assertEqual("LDOO_EJ_19", a.repo)
        a = sb.build_student("1186622", LDOO, "github.com/ppgodel/lol")
        self.assertEqual("LDOO_EJ_19", a.repo)

    def test_from_file(self):
        columns = ["Matricula", "Nombre", "Primer apellido", "Segundo apellido", "Grupo"]
        a = CourseBuilder.build_course_from_csv("test/resources/students.csv", 'direccion de tu repositorio GIT', columns)
        a.to_csv('test/resources/LDOO_repos.csv', sep=',', encoding='utf-8', index=False)
        self.assertIsNotNone(a)
        #import pandas
