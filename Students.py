import re
import pandas as pd
import requests
import datetime

LDOO = 'LDOO'
LBD = 'LBD'
name = 'Name'

possible_repositories = dict(LDOO=["LDOO_EJ_19", "LDOO", "LDOO_EJ_2019", "LDOO_Enero_Julio_19",
                                   "LDOO_Enero_Julio_2019"],
                             LBD=['LBD', 'BD', 'BaseDeDatos'])


class Course:
    name: str

    def __init__(self, name):
        self.name = name


class Student:
    student_id: str
    name: str
    first_name: str
    second_name: str
    gender: str

    def __init__(self, student_id, name, first_name, second_name, gender, age):
        self.student_id = student_id
        self.name = name
        self.first_name = first_name
        self.second_name = second_name
        self.gender = gender
        self.age = age


class ClassMate:
    student_id: str
    class_name: str
    site: str
    user: str
    repo: str

    def __init__(self, student_id, class_name, site, user, repo):
        self.student_id = student_id
        self.class_name = class_name
        self.site = site
        self.user = user
        self.repo = repo

    def get_repository_list(self):
        return RepositoryQuerier.get_repository_list_by(self.site, self.user, 'name')


class RepositoryQuerier:
    auth_user: str
    auth_pass: str

    def __init__(self, auth_user: str, auth_pass: str):
        self.auth_user = auth_user
        self.auth_pass = auth_pass

    @staticmethod
    def get_parameters(**params):
        parameters = None
        if params:
            parameters = "&".join([f"{k}={v}" for (k, v) in params.items()])
        return parameters

    @staticmethod
    def get_base_url(url_template: str, **kwargs):
        return url_template.format(**kwargs)

    @staticmethod
    def get_url(base_url: str, params: str):
        return "{base}?{parameters}".format(base=base_url, parameters=params)

    def get_repository_list(self, site: str, user: str):
        base_url = RepositoryQuerier.get_base_url("https://api.{site}/users/{user}/repos",
                                           **{"site": site, "user": user})
        parameters = RepositoryQuerier.get_parameters(**{"user": self.auth_user, "pwd": self.auth_pass})
        url = RepositoryQuerier.get_url(base_url, parameters)
        return RepositoryQuerier.get_response_json(url)

    @staticmethod
    def get_response_json(url):
        response = requests.get(url)
        json = None
        if response.status_code >= 200 <= 250:
            json = response.json()
        return json

    @staticmethod
    def get_response_content(download_url):
        content = None
        response = requests.get(download_url)
        if response.status_code >= 200 <= 250:
            content = response.content
        return content

    def get_commit_list_of_a_file(self, site, user, repo, file_path):
        base_url = RepositoryQuerier.get_base_url("https://api.{site}/repos/{user}/{repo}/commits", **{"site": site, "user": user, "reop": repo})
        params = RepositoryQuerier.get_parameters(**{"user": self.auth_user, "pwd": self.auth_pass, "path": file_path})
        url = RepositoryQuerier.get_url(base_url,params)
        return RepositoryQuerier.get_response_json(url)

    @staticmethod
    def get_file_info(site, user, repo, file_path):
        url = "https://apih.{site}/repos/{user}/{repo}/contents/{file}". \
            format(site=site, user=user, repo=repo, file=file_path)
        return RepositoryQuerier.get_response_json(url)

    @staticmethod
    def get_file(site, user, repo, file_path):
        file_info = RepositoryQuerier.get_file_info(site, user, repo, file_path)
        if not file_info or len(file_info) > 1:
            return None
        download_url = file_info.get('download_url')
        return RepositoryQuerier.get_response_content(download_url)

    @staticmethod
    def get_repository_list_by(site: str, user: str, prop: str):
        repo_list = RepositoryQuerier.get_repository_list(site, user)
        if not repo_list:
            return None
        return [x.get(prop) for x in repo_list]


def process_df(students_df: pd.DataFrame, git_column: str):
    return students_df.apply(lambda row: StudentBuilder.get_repo_info(row.get(git_column), LBD),
                             axis='columns', result_type='expand')


def review_student_practice(repo_site: str, repo_user: str, repo_name: str, practice_obj: dict):
    p_due_date = datetime.datetime.strptime(practice_obj.get('due_date'), "%Y-%m-%d %H:%M")
    calif = None
    file_name = None
    for poss_name in practice_obj.get('possible_name'):
        commit_list = RepositoryQuerier.get_commit_list_of_a_file(repo_site, repo_user, repo_name, poss_name)
        if commit_list:
            file_name = poss_name
            break
    if not commit_list:
        if datetime.datetime.now() < p_due_date:
            return calif
        else:
            return 0
    first_commit = commit_list[len(commit_list) - 1]['commiter']['date']
    first_commit_date = datetime.datetime.strptime(first_commit, "%Y-%m-%dT%H:%M:%sZ")
    if first_commit_date < p_due_date:
        calif = practice_obj.get('due_value')
    else:
        calif = 0
    # eval_list = practice_obj.get('review_rules')
    # file_to_review = RepositoryQuerier.get_file(repo_site,repo_user, repo_name, file_name)
    # for eval_rule in eval_list:
    #    matches = re.search(eval_rule.get('regex'), file_to_review)
    #    if matches:
    #        eval_code = matches.group(eval_rule.get('group'))
    #        eval_code.split(',')
    return calif


def review_practice(students_df: pd.DataFrame, practice_dict: dict):
    return_value = students_df.apply(lambda row: review_student_practice(
        row.get('repo_site', 'repo_user', 'repo_name', practice_dict)),
                                     axis='columns', result_type='expand')
    return return_value


class CourseBuilder:
    @staticmethod
    def build_course_from_csv(csv_path: str, git_column: str, columns: list):
        students_df = pd.read_csv(csv_path)
        dfr = process_df(students_df, git_column)
        dfr.columns = ['repo_site', 'repo_user', 'repo_name']
        base_df = students_df.loc[:, columns]
        new_df = pd.concat([base_df, dfr], axis=1)
        return new_df

    # @staticmethod
    # def build_course_from_csv(csv_path: str, practice_dict: dict):
    #     students_df = pd.read_csv(csv_path)
    #     dfr = review_practice(students_df, practice_dict)


class StudentBuilder:
    def __init__(self, auth_user: str, auth_pass: str):
        querier = RepositoryQuerier(auth_user, auth_pass)

    def build_student(self, matricula: str, class_name: str, url: str):
        site, user, repo, = self.get_repo_info(url, class_name)
        class_mate = ClassMate(matricula, class_name, site, user, repo) if site and user else None
        return class_mate

    def get_repo_info(self, url: str, class_name: str):
        site = user = repo = None
        try:
            base_url = StudentBuilder._remove_protocol_from_url(url)
            url_pieces = base_url.split('/')
            pieces = len(url_pieces)
            if pieces > 1 and url_pieces[0] and url_pieces[1]:
                site = StudentBuilder._format_site(url_pieces[0])
                user = url_pieces[1]
                if pieces > 2 and url_pieces[2]:
                    repo = StudentBuilder._format_repo(url_pieces[2])
        except Exception as e:
            print("No valid repo for {}, {}".format(url, e))
        return self._validate_repository(site, user, repo, class_name)

    @staticmethod
    def _format_repo(repo_raw: str):
        repo_pieces = repo_raw.split('.')
        return repo_pieces[0]

    @staticmethod
    def _format_site(site):
        formatted_site = None
        site_pieces = site.split('.')
        sp_len = len(site_pieces)
        if sp_len > 1:
            formatted_site = site_pieces[sp_len - 2] + '.' + site_pieces[sp_len - 1]
        return formatted_site

    @staticmethod
    def _remove_protocol_from_url(url: str):
        return_url = url
        is_match = re.match('https?://', url)
        if is_match:
            return_url = url.replace(is_match.group(0), '')
        return return_url

    def _validate_repository(self, site, user, repo, class_name):
        validated_site = validated_user = validated_repo = repo_list = None
        if site and user:
            repo_list = self.querier.get_repository_list_by(site, user, 'name')
        if repo_list:
            validated_site = site
            validated_user = user
            validated_repo = repo if repo in repo_list else \
                StudentBuilder.search_valid_repository(class_name, repo_list)
        return validated_site, validated_user, validated_repo

    @staticmethod
    def search_valid_repository(class_name, repo_list):
        validated_repo = None
        for x in possible_repositories.get(class_name):
            if x in repo_list:
                validated_repo = x
                break
        return validated_repo
