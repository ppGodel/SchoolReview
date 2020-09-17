import requests
import re
from typing import List

def generate_practice_name_list_from_template_number(practice_name_template: List[str],
                                                     practice_number: int) -> List[str]:
    result = [x + str(practice_number) for x in practice_name_template]
    if practice_number < 10:
        [result.append(x + "0" + str(practice_number)) for x in practice_name_template]
    return result

local_practice_names = ["Practica", "P", "Tarea", "Ejercicio", "P"]
possible_repositories_names = ["/LDOO_EJ_19", "/LDOO", "/LDOO_EJ_2019", "/LDOO_Enero_Julio_19", "/LDOO_Enero_Julio_2019"]

def generate_practice_name_list_from_local(practice_number: int) -> List[str]:
    return generate_practice_name_list_from_template_number(local_practice_names, practice_number)


def repository_formatter(repo):
    links_to_test = []
    if repo is not None and repo != "":
        if not repo.startswith('http'):
            repo = 'https://' + repo
        match_complete_repo = re.search(r"https?://(\w*\.)+\w*/\w*/\w*", repo, re.M | re.I)
        if match_complete_repo:
            links_to_test.append(repo)
        else:
            match_user = re.search(r"https?://(\w*\.)+\w*/\w*", repo, re.M | re.I)
            if match_user:
                [links_to_test.append(repo + x) for x in possible_repositories_names]
    return links_to_test


def repository_check(repo):
    result = False
    if repo is not None and repo != "":
        if not repo.startswith('http'):
            repo = 'https://' + repo
        match_complete_repo = re.search(r"https?://(\w*\.)+\w*/\w*/\w*", repo, re.M | re.I)
        if match_complete_repo:
            request = requests.get(repo)
            if request.status_code == 200:
                result = True
    return result


def get_repository(url):
    result = ""
    repo_list = repository_formatter(url)
    if len(repo_list) == 1 and repository_check(repo_list[0]):
        result = repo_list[0]
    else:
        for x in repo_list:
            if repository_check(x):
                result = x
                break
    return result


def practice_checker(url, practice):
    result = False
    repo = get_repository(url)
    if repo != "":
        for practice_name in generate_practice_name_list_from_local(practice):
            practice_to_check = repo + "/blob/master/" + practice_name
            print(practice_to_check)
            request = requests.get(practice_to_check)
            if request.status_code == 200:
                result = True
                break
    return result


def check_equal(arr1, arr2):
    return len(arr1) == len(arr2) and sorted(arr1) == sorted(arr2)


