from enum import Enum
from importlib.metadata import version
from pathlib import Path

import click
from codeowners import CodeOwners
from halo import Halo

from refactor_stats_maker.repository_helpers import RepoHandler
from refactor_stats_maker.stats_helpers import (
    build_chart_data,
    BasicOracle,
    build_file_status_list,
    build_leaderboard_data,
    build_stats_data,
)
from refactor_stats_maker.stats_helpers import (
    display_chart,
    display_commits,
    display_leaderboard,
    display_team_assignments,
)
from refactor_stats_maker.stats_helpers import get_file_owners


class StatsType(Enum):
    EXPANDS = "expands"
    CLASS_BASED = "class-based"


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


def get_team_assignments(
    files: list[str], codeowners: CodeOwners
) -> dict[str, list[str]]:
    # ASSIGN EACH FILE TO A TEAM

    team_assignments: dict[str, list[str]] = {}

    for file_to_refactor in files:
        teams = get_file_owners(file_to_refactor, codeowners)
        for team in teams:
            assigned_files = team_assignments.get(team, [])
            team_assignments[team] = assigned_files + [file_to_refactor]

    return team_assignments


def get_scan_args(stats_type: StatsType) -> tuple[str, str]:
    match stats_type.value:
        case "expands":
            return "a4c5abe006e7b55ecdab72bf6e997118cc6e60e6", "expanded: [',\\[].*"
        case "class-based":
            return "74d716e70263ffb017171a39a5a0e724c02356b3", "@Component"
    raise Exception("Invalid type for commit hash")


@click.command()
@click.version_option(version=version("refactor_stats_maker"))
@click.argument("repository-path", nargs=1, type=click.Path(exists=True))
@click.option(
    "-l", "--file-list", default=False, is_flag=True, help="Display file list."
)
@click.option(
    "-c", "--copy", default=False, is_flag=True, help="Copy output to clipboard."
)
@click.option(
    "-g",
    "--gitlab",
    default=False,
    is_flag=True,
    help="Format output in GitLab flavored Markdown.",
)
@click.option("--leaderboard", default=False, is_flag=True, help="Display leaderboard")
@click.option("--list-commits", default=False, is_flag=True, help="Display commit list")
@click.option("--stats", default=False, is_flag=True, help="Display statistics.")
@click.option(
    "-t",
    "--type",
    default="expands",
    type=click.Choice(["expands", "class-based"], case_sensitive=False),
    help="Type of statistics to generate.",
)
def run(
    repository_path: Path,
    file_list: bool,
    copy: bool,
    gitlab: bool,
    leaderboard: bool,
    list_commits: bool,
    stats: bool,
    type: str,
):
    repo_path = repository_path
    verbose = file_list
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

    working_repo_handler = RepoHandler(repo_path)

    # LET THE USER KNOW WHAT I'M ABOUT TO DO
    click.secho(f"Generating statistics for {project_name}", fg="green")

    # LOOK FOR FILES TO REFACTOR

    commit_hash = get_scan_args(stats_type)[0]
    regex = get_scan_args(stats_type)[1]
    exclude = ["spec.ts", "stories.ts", "md"]
    current_files = working_repo_handler.get_files_to_refactor(regex, exclude=exclude)
    baseline_files = working_repo_handler.get_baseline_file_paths(
        commit_hash, regex, exclude=exclude
    )
    codeowners = get_codeowners(repo_path)

    # compare each file list and return a list of File status objects
    status_files = build_file_status_list(baseline_files, current_files)

    if leaderboard or list_commits:
        working_repo_handler.move_to_baseline_commit("develop", pull=True)
        commits = working_repo_handler.get_commits_since_hash(commit_hash)
        spinner = Halo(text="Inspecting commits...", spinner="dots")
        spinner.start()
        stats_data = build_stats_data(commits, regex, baseline_files)
        spinner.stop()

        if list_commits:
            # DISPLAY A LIST OF RELEVANT COMMITS
            display_commits(
                sorted(stats_data, key=lambda commit: commit.date, reverse=True)
            )
        if leaderboard:
            # DISPLAY A LEADERBOARD
            display_leaderboard(build_leaderboard_data(stats_data))

        if stats:
            # DISPLAY REMAINING REFACTORS OVER TIME
            data = build_chart_data(stats_data)
            display_chart(data)

            print()

            # DISPLAY END DATE ESTIMATES
            estimates = BasicOracle.make_prediction(data)
            BasicOracle.display_estimates(estimates)

    # DRAW A TIMELINE OF REFACTORS LEFT

    # plt.date_form('Y/m/d')
    # plt.clc()
    # plt.plotsize(100, 10)
    # plt.plot(dates, refactors_left)
    # plt.title("Refactors left since epoch")
    # plt.xlabel("Date")
    # plt.ylabel("Refactors left")
    # plt.show()
    #
    # fig = px.line(x=dates, y=refactors_left, title='Cenas')
    # fig.show()

    display_team_assignments(
        project_name,
        status_files,
        codeowners,
        verbose=verbose,
        copy_to_clipboard=copy_to_clipboard,
        format_for_gitlab=format_for_gitlab,
    )


if __name__ == "__main__":
    run()
