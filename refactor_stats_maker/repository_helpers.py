import hashlib
from pathlib import Path

import platformdirs
from git import InvalidGitRepositoryError, Repo, Commit
from halo import Halo
from ripgrepy import Ripgrepy


def hash_root_repo_path(path: str) -> str:
    return hashlib.md5(str.encode(path)).hexdigest()


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
        self.cache_repo_root = Path(cache_repo_root_str).joinpath(
            hash_root_repo_path(self.root_repo.git_dir.__str__()))

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
            remote = self.get_repo_remote_origin()
            spinner = Halo(text="Cloning the repository into cache", spinner="dots")
            spinner.start()
            repo = Repo.clone_from(remote, str(self.cache_repo_root))
            spinner.stop()
        return repo

    def move_to_baseline_commit(self, commit_hash: str, pull=True):
        git = self.cache_repo.git
        if pull:
            spinner = Halo(text="Fetching commits...", spinner="dots")
            spinner.start()
            git.reset('--hard')
            git.checkout(self.root_repo.active_branch.name)
            git.fetch()
            git.pull()
            spinner.stop()
        spinner = Halo(text="Moving to baseline commit", spinner="dots")
        spinner.start()
        git.checkout(commit_hash)
        spinner.stop()

    def get_commits_since_hash(self, commit_hash: str) -> list[Commit]:
        commits: list[Commit] = []
        for commit in list(self.cache_repo.iter_commits()):
            # maybe there's a better way to determine if a commit is a merge commit
            if not commit.summary.startswith('Merge'):
                commits.append(commit)
            if commit.hexsha == commit_hash:
                return commits
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
