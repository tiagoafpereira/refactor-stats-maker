import sys
from pathlib import Path
from typing import List

from codeowners import CodeOwners
from ripgrepy import Ripgrepy

from refactor_stats_maker.repository_helpers import clone_repo_at_baseline
from refactor_stats_maker.stats_helpers import build_file_status_list
from refactor_stats_maker.stats_helpers import display_team_assignments
from refactor_stats_maker.stats_helpers import get_file_owners


def get_files_to_refactor(
        repo_path: str, regex: str, exclude: List[str] = []
) -> List[str]:
    src_path = str(Path(f"{repo_path}").expanduser())
    rg = Ripgrepy(regex, src_path)

    # SEE https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md#manual-filtering
    # -globs
    excluded_extensions_glob = ",".join(exclude)
    excluded_extensions_glob = f"!*.{{{excluded_extensions_glob}}}"

    files_to_refactor = (
        rg.glob(excluded_extensions_glob).files_with_matches().run().as_string
    )

    lines = files_to_refactor.split("\n")

    lines = [f.replace(src_path + "/", "src/") for f in lines if f != ""]

    return lines


def get_codeowners(repo_path) -> CodeOwners:
    # PARSE CODEOWNERS FILE
    codeowners_file = Path(f"{repo_path}/CODEOWNERS").expanduser()

    try:
        with codeowners_file.open() as f:
            codeowners = CodeOwners(f.read())
            return codeowners
    except IOError:
        print(
            f"Cannot find a CODEOWNERS file "
            f"are you sure WebCoreClient is located in {repo_path}"
        )
        exit(1)


def get_team_assignments(files: List[str], codeowners: CodeOwners):
    # ASSIGN EACH FILE TO A TEAM

    team_assignments = {}

    for file_to_refactor in files:
        teams = get_file_owners(file_to_refactor, codeowners)
        for team in teams:
            assigned_files = team_assignments.get(team, [])
            team_assignments[team] = assigned_files + [file_to_refactor]

    return team_assignments


def get_scan_args(type: str) -> tuple[str, str]:
    match type:
        case "expands":
            return "a4c5abe006e7b55ecdab72bf6e997118cc6e60e6", "expanded: [',\\[].*"
        case "class-based":
            return "74d716e70263ffb017171a39a5a0e724c02356b3", "@Component"
    raise Exception("Invalid type for commit hash")


def run():
    repo_path = None
    verbose = False
    copy_to_clipboard = False
    format_for_gitlab = False
    args = []

    match sys.argv:
        case [_]:
            print("Empty repository path")
            exit(1)
        case [_, path]:
            repo_path = path
        case [_, path, *args]:
            repo_path = path
            args = args

    verbose = "-v" in args
    copy_to_clipboard = "--copy" in args
    format_for_gitlab = "--gitlab" in args
    refactor_type = "expands"
    if "--expands" in args:
        refactor_type = "expands"
    if "--class-based" in args:
        refactor_type = "class-based"

    # VALIDATE THE REPOSITORY PATH
    if repo_path is None:
        print("Invalid repository path")
        exit(1)

    # LOOK FOR FILES TO REFACTOR

    src_path = Path(repo_path + "/src").expanduser()
    print(src_path)
    commit_hash = get_scan_args(refactor_type)[0]
    regex = get_scan_args(refactor_type)[1]
    exclude = ["spec.ts", "stories.ts"]
    # regex =
    current_files = get_files_to_refactor(src_path, regex, exclude=exclude)
    baseline_files = get_baseline_file_paths(
        commit_hash, regex, exclude=exclude)
    codeowners = get_codeowners(repo_path)

    # compare each file list and return a list of File status objects
    status_files = build_file_status_list(
        baseline_files, current_files)

    display_team_assignments(
        status_files,
        codeowners,
        verbose=verbose,
        copy_to_clipboard=copy_to_clipboard,
        format_for_gitlab=format_for_gitlab,
    )


def get_baseline_file_paths(commit_hash, regex, exclude) -> list[str]:
    working_dir = clone_repo_at_baseline(
        commit_hash) + "/src"
    files = get_files_to_refactor(working_dir, regex, exclude)
    return files


if __name__ == "__main__":
    run()
