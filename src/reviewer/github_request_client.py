import urllib.parse
from functools import lru_cache
from typing import List, Dict, Optional, Union

from src.utils.url import get_base_url, map_parameters, get_url, get_response_json, get_response_content


@lru_cache(maxsize=None)
def github_get_commit_list_of_a_file(client_id: str, client_secret: str, site, user, repo, file_path) -> List[Dict]:
    base_url = get_base_url("https://api.{site}/repos/{user}/{repo}/commits",
                            **{"site": site, "user": user, "repo": repo})
    parameters = map_parameters(
        **{"client_id": client_id, "client_secret": client_secret, "path": file_path})
    url = get_url(base_url, parameters)
    return get_response_json(url)


@lru_cache(maxsize=None)
def github_get_file_info(client_id: str, client_secret: str, site: str, user: str, repo: str, file_path: str) -> \
        Optional[Union[List[Dict], Dict]]:
    base_url = "https://api.{site}/repos/{user}/{repo}/contents/{file}". \
        format(site=site, user=user, repo=urllib.parse.quote(repo), file=urllib.parse.quote(file_path))
    parameters = map_parameters(**{"client_id": client_id, "client_secret": client_secret})
    url = get_url(base_url, parameters)
    return get_response_json(url)


def github_get_file(client_id: str, client_secret: str, site: str, user: str, repo: str, file_path: str) -> Optional[
    bytes]:
    file_info = None
    try:
        file_info = github_get_file_info(client_id, client_secret, site, user, repo, file_path)
    except Exception as e:
        print("Error found at get file from url {}".format(e))
    if not file_info:
        return None
    download_url = file_info['download_url']
    return get_response_content(download_url)


@lru_cache(maxsize=None)
def github_get_repository_list(client_id: str, client_secret: str, site: str, user: str) -> Dict:
    base_url = get_base_url("https://api.{site}/users/{user}/repos",
                            **{"site": site, "user": user})
    parameters = map_parameters(**{"client_id": client_id, "client_secret": client_secret})
    url = get_url(base_url, parameters)
    return get_response_json(url)


def github_get_repository_list_by(client_id: str, client_secret: str, site: str, user: str, prop: str) \
        -> Optional[List[str]]:
    repo_list = github_get_repository_list(client_id, client_secret, site, user)
    if not repo_list:
        return None
    try:
        return [x.get(prop) for x in repo_list]
    except AttributeError:
        print("site: {}, git_user: {}, property: {}".format(site, user, prop))
