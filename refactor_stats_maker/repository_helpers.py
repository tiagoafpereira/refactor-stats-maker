import time
from pathlib import Path

import platformdirs
from git import InvalidGitRepositoryError, Repo, Commit
from halo import Halo

repo_root = platformdirs.user_cache_dir("refactor_stats_maker", "Tiago Pereira")
repo_root = Path(repo_root).joinpath("wcc")


def create_repo_root():
    if not repo_root.exists():
        # create repository folder
        Path.mkdir(repo_root, parents=True)


def get_repo_remote_origin(repo: Repo) -> str:
    config = repo.config_reader()
    return config.get('remote "origin"', "url")


def clone_repo() -> Repo:
    create_repo_root()

    # clone the repository onto the user's cache folder
    try:
        repo = Repo(repo_root)
    except InvalidGitRepositoryError:
        spinner = Halo(text="Cloning the repository", spinner="dots")
        spinner.start()
        repo = Repo.clone_from(
            "git@gitlab.com:infraspeak/web/web-core-client.git", repo_root
        )
        spinner.stop()

    return repo


def move_to_baseline_commit(repo: Repo, commit_hash: str, fetch=True):
    git = repo.git
    if fetch:
        spinner = Halo(text="Fetching commits...", spinner="dots")
        spinner.start()
        git.fetch()
        spinner.stop()
    spinner = Halo(text="Moving to baseline commit", spinner="dots")
    spinner.start()
    git.checkout(commit_hash)
    spinner.stop()


def clone_repo_at_baseline(commit_hash: str) -> Path:
    repo = clone_repo()
    move_to_baseline_commit(repo, commit_hash)
    return Path(repo.working_dir)


def get_commits_since_hash(repo: Repo, commit_hash: str) -> list[Commit]:
    commits = []
    day = 0
    for commit in list(repo.iter_commits("develop")):
        if commit.hexsha == commit_hash:
            print('DONE!')
            break
        current_day = time.gmtime(commit.committed_date).tm_mday
        if not day:
            day = current_day
            print('first day', day)

        if day == current_day:
            continue
        else:
            day = current_day
            print('update day', day)

        summary = str(commit.summary)
        # print(summary)
        # if summary.startswith('Merge branch'):
        #     continue

        date = time.strftime("%a, %d %b %Y %H:%M",
                             time.gmtime(commit.committed_date))
        print(f'{commit.hexsha} {date} {commit.summary}')
        commits.insert(len(commits), commit)
    return commits
