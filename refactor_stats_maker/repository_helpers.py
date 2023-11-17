from pathlib import Path

import platformdirs
from git import InvalidGitRepositoryError, Repo
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


def move_to_baseline_commit(repo: Repo, commit_hash: str):
    git = repo.git
    spinner = Halo(text="Fetching commits...", spinner="dots")
    spinner.start()
    git.fetch()
    spinner.stop()
    spinner = Halo(text="Moving to baseline commit", spinner="dots")
    spinner.start()
    git.checkout(commit_hash)
    spinner.stop()


def clone_repo_at_baseline(commit_hash: str) -> str:
    repo = clone_repo()
    move_to_baseline_commit(repo, commit_hash)
    return str(repo.working_dir)
