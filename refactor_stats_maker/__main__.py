from enum import Enum
from importlib.metadata import version
from pathlib import Path
from typing import List

import click
from codeowners import CodeOwners
from ripgrepy import Ripgrepy

from refactor_stats_maker.repository_helpers import clone_repo_at_baseline
from refactor_stats_maker.stats_helpers import build_file_status_list, \
    display_team_assignments, get_file_owners


class StatsType(Enum):
    EXPANDS = "expands"
    CLASS_BASED = "class-based"


def get_files_to_refactor(
        repo_path: Path, regex: str, exclude: List[str] = []
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


def get_scan_args(type: StatsType) -> tuple[str, str]:
    match type.value:
        case "expands":
            return "a4c5abe006e7b55ecdab72bf6e997118cc6e60e6", "expanded: [',\\[].*"
        case "class-based":
            return "74d716e70263ffb017171a39a5a0e724c02356b3", "@Component"
    raise Exception("Invalid type for commit hash")


@click.command()
@click.version_option(version=version('refactor_stats_maker'))
@click.argument('repository-path', nargs=1, type=click.Path(exists=True))
@click.option('-l', '--list', default=False, is_flag=True, help='Display file list.')
@click.option('-c', '--copy', default=False, is_flag=True,
              help='Copy output to clipboard.')
@click.option('-g', '--gitlab', default=False,
              is_flag=True,
              help='Format output in GitLab flavored Markdown.')
@click.option('-t', '--type', default='expands',
              type=click.Choice(['expands', 'class-based'], case_sensitive=False),
              help='Type of statistics to generate.')
def run(repository_path: Path, list: bool, copy: bool, gitlab: bool, type: str):
    repo_path = repository_path
    verbose = list
    copy_to_clipboard = copy
    format_for_gitlab = gitlab

    stats_type = StatsType.EXPANDS  # default
    project_name = ""
    match type:
        case "expands":
            stats_type = StatsType.EXPANDS
            project_name = "Old Expands"
        case "class-based":
            project_name = "Class Based to Options API"
            stats_type = StatsType.CLASS_BASED

    # VALIDATE THE REPOSITORY PATH
    if repo_path is None:
        print("Invalid repository path")
        exit(1)

    # LET THE USER KNOW WHAT I'M ABOUT TO DO
    click.secho(f"Generating statistics for {project_name}", fg='green')

    # LOOK FOR FILES TO REFACTOR

    src_path = Path(repo_path).joinpath("src")

    commit_hash = get_scan_args(stats_type)[0]
    regex = get_scan_args(stats_type)[1]
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
        project_name,
        status_files,
        codeowners,
        verbose=verbose,
        copy_to_clipboard=copy_to_clipboard,
        format_for_gitlab=format_for_gitlab,
    )


def get_baseline_file_paths(commit_hash, regex, exclude) -> list[str]:
    working_dir = clone_repo_at_baseline(
        commit_hash).joinpath("src")
    files = get_files_to_refactor(working_dir, regex, exclude)
    return files


if __name__ == "__main__":
    run()
