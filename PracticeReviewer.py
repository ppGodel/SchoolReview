import pandas as pd
from functools import partial
from Students import RepositoryQuerier


def read_csv(csv_path: str):
    students_df = pd.read_csv(csv_path)
    return students_df


def review_practice_time(rq: RepositoryQuerier, repo_site: str, git_user: str, git_repo: str,
                         practice: str):
    return rq.get_file_info(repo_site, git_user, git_repo, practice)

def review_practice_from_df(df: pd.DataFrame, rq: RepositoryQuerier, practice: str):
    rvp = partial(review_practice_time, rq)
    df.apply(lambda row: rvp(row.get("repo_site"), row.get("repo_user"), row.get("repo_name"), practice), axis=1)

