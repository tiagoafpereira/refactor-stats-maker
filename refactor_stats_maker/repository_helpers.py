import time
from pathlib import Path

import platformdirs
from git import InvalidGitRepositoryError, Repo, Commit
from halo import Halo
from ripgrepy import Ripgrepy


class RepoHandler:
    root_repo_path: Path | None = None
    root_repo: Repo
    cache_repo_root: Path | None = None
    cache_repo: Repo

    def __init__(self, root: Path):

        self.root_repo_path = root
        self.root_repo = Repo(self.root_repo_path)

        # create a clone of the repository in cache
        cache_repo_root_str: str = platformdirs.user_cache_dir("refactor_stats_maker",
                                                               "Tiago Pereira")
        self.cache_repo_root = Path(cache_repo_root_str).joinpath("wcc")
        self.cache_repo = self.clone_cache_repo()

    def create_cache_repo_root_folder(self):
        if not self.cache_repo_root.exists():
            # create repository folder
            Path.mkdir(self.cache_repo_root, parents=True)

    def get_repo_remote_origin(self) -> str:
        config = self.root_repo.config_reader()
        return config.get('remote "origin"', "url")

    def clone_cache_repo(self) -> Repo:
        self.create_cache_repo_root_folder()

        # clone the repository onto the user's cache folder
        try:
            repo = Repo(self.cache_repo_root)
        except InvalidGitRepositoryError:
            spinner = Halo(text="Cloning the repository", spinner="dots")
            spinner.start()
            repo = Repo.clone_from(self.get_repo_remote_origin(),
                                   str(self.cache_repo_root))
            spinner.stop()

        return repo

    def move_to_baseline_commit(self, commit_hash: str, fetch=True):
        git = self.cache_repo.git
        if fetch:
            spinner = Halo(text="Fetching commits...", spinner="dots")
            spinner.start()
            git.fetch()
            spinner.stop()
        spinner = Halo(text="Moving to baseline commit", spinner="dots")
        spinner.start()
        git.checkout(commit_hash)
        spinner.stop()

    def get_commits_since_hash(self, repo: Repo, commit_hash: str) -> list[Commit]:
        commits: list[Commit] = []
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

    def get_baseline_file_paths(self, commit_hash, regex, exclude) -> list[str]:
        working_dir = Path(self.cache_repo.working_dir)
        self.move_to_baseline_commit(commit_hash)
        files = self.get_files_to_refactor_in_folder(working_dir, regex, exclude)
        return files

    @staticmethod
    def get_files_to_refactor_in_folder(repo_path: Path, regex: str,
                                        exclude: list[str] = []
                                        ) -> list[str]:
        src_path = str(Path(f"{repo_path}").expanduser())
        rg = Ripgrepy(regex, src_path)

        # SEE https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md#manual
        # -filtering
        # -globs
        excluded_extensions_glob = ",".join(exclude)
        excluded_extensions_glob = f"!*.{{{excluded_extensions_glob}}}"

        files_to_refactor = (
            rg.glob(excluded_extensions_glob).files_with_matches().run().as_string
        )

        lines = files_to_refactor.split("\n")

        lines = [f.replace(src_path + "/src/", "src/") for f in lines if f != ""]

        return lines

    def get_files_to_refactor(self, regex: str, exclude=None) -> list[str]:
        if not exclude:
            exclude = []
        if not self.root_repo_path:
            raise Exception('Invalid repository root')
        return self.get_files_to_refactor_in_folder(self.root_repo_path, regex, exclude)
