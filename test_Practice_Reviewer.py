import json
from unittest import TestCase
from functools import partial
from Students import RepositoryQuerier
import PracticeReviewer


class TestTest(TestCase):
    def _arrange(self):
        with open('test/resources/my_data.json') as f:
            my_data = json.load(f)
        self.rq = RepositoryQuerier(my_data["client_id"], my_data["client_secret"])

    def test_con(self):
        self._arrange()
        file = self.rq.get_file("github.com", "ppgodel", "SchoolReview", "test/resources/practicas.csv")
        assert file
