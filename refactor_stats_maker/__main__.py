import re
import time
from datetime import date, datetime
from enum import Enum
from importlib.metadata import version
from itertools import chain
from pathlib import Path
from typing import List

import click
from codeowners import CodeOwners
from git import Commit, Actor
from halo import Halo
from rich import box
from rich.console import Console
from rich.table import Table

from refactor_stats_maker.repository_helpers import RepoHandler
from refactor_stats_maker.stats_helpers import build_file_status_list, \
    display_team_assignments, get_file_owners


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


def build_leaderboard_data(commits: list[Commit], regex: str) -> tuple[
    dict[Actor, int], list[Commit]]:
    regex_expr = re.compile(regex)

    # GET REFACTORS LEFT PER COMMIT
    refactors_left = []
    dates = []

    authors: dict[Actor, int] = {}
    relevant_commits = []

    for commit in commits:
        diff = commit.diff(commit.parents)

        # look at modified M and deleted D files to check for applied refactors
        for d in chain(diff.iter_change_type("M"), diff.iter_change_type("D")):

            # ignore files that we know won't have any refactors applied
            if not d.a_path.endswith('vue') and not d.a_path.endswith('ts'):
                continue

            before_text = ""
            after_text = d.a_blob.data_stream.read().decode()
            deleted_matches = 0
            try:
                before_text = d.b_blob.data_stream.read().decode()
            except AttributeError:
                deleted_matches = len(regex_expr.findall(after_text))
            matches_before = len(regex_expr.findall(before_text))
            matches_after = len(regex_expr.findall(after_text))
            diff_matches = matches_before - matches_after
            if diff_matches > 0:
                # print(datetime.fromtimestamp(commit.committed_date).strftime(
                #     "%Y/%m/%d"))
                if commit not in relevant_commits:
                    relevant_commits.append(commit)
                authors[commit.author] = (authors.get(commit.author, 0)
                                          + diff_matches +
                                          deleted_matches)
        # working_repo_handler.move_to_baseline_commit(repo, commit.hexsha, fetch=False)
        # time.sleep(1)
        # files_to_refactor = get_files_to_refactor(repo.working_dir, regex, exclude)
        # status_files = build_file_status_list(baseline_files, files_to_refactor)
        # data = build_report_data(status_files, codeowners)
        # team_names = data[2]
        # percentages = data[3]
        # date = time.strftime("%a, %d %b %Y %H:%M", time.gmtime(commit.committed_date))
        # chart_date = time.strftime("%Y/%m/%d", time.gmtime(commit.committed_date))
        # refactors_left.append(len(files_to_refactor))
        # dates.append(chart_date)
        # print(f'{date} {commit.summary}: {len(files_to_refactor)}')

    relevant_commits = sorted(relevant_commits, key=lambda item: item.committed_date,
                              reverse=True)

    return authors, relevant_commits


def display_commits(commits: list[Commit]):
    table = Table(title="Commits in reverse chronological order", box=box.SIMPLE_HEAD)

    table.add_column("Author", style="#1FB0FF", justify="right")
    table.add_column("Date")
    table.add_column("Summary")

    for commit in commits:
        table.add_row(
            commit.author.name,
            time.strftime("%a, %d %b %Y %H:%M", time.gmtime(commit.committed_date)),
            commit.summary)

    console = Console()
    console.print(table)
    return


def display_leaderboard(authors: dict[Actor, int]):
    start = datetime(day=1, month=12, year=date.today().year).date()
    end = datetime(day=31, month=12, year=date.today().year).date()
    xmas_style = start <= date.today() <= end
    xmas_tree = "\N{christmas tree}"
    santa = "\U0001F385"
    gift = "\U0001F381"

    match xmas_style:
        case True:
            title = f"{xmas_tree} LEADERBOARD {santa}"
            author_color = "red1"
            refactors_color = "green1"
        case _:
            title = "LEADERBOARD"
            author_color = "#808080"
            refactors_color = "#1FB0FF"

    # DISPLAY A LEADERBOARD
    authors = dict(sorted(authors.items(), key=lambda item: item[1], reverse=True))

    table = Table(title=title)

    table.add_column("Author", justify="right", style=author_color, no_wrap=True)
    table.add_column("Refactor count", style=refactors_color)

    keys = list(authors.keys())
    for author, refactors in authors.items():
        index = keys.index(author)
        if index == 0 and xmas_style:
            name = f"{gift} {author.name}"
        else:
            name = author.name or ""
        table.add_row(name, str(refactors))

    console = Console()
    console.print(table)


@click.command()
@click.version_option(version=version('refactor_stats_maker'))
@click.argument('repository-path', nargs=1, type=click.Path(exists=True))
@click.option('-l', '--list', default=False, is_flag=True, help='Display file list.')
@click.option('-c', '--copy', default=False, is_flag=True,
              help='Copy output to clipboard.')
@click.option('-g', '--gitlab', default=False,
              is_flag=True,
              help='Format output in GitLab flavored Markdown.')
@click.option('--leaderboard', default=False,
              is_flag=True,
              help='Display leaderboard')
@click.option('--list-commits', default=False,
              is_flag=True,
              help='Display commit list')
@click.option('-t', '--type', default='expands',
              type=click.Choice(['expands', 'class-based'], case_sensitive=False),
              help='Type of statistics to generate.')
def run(repository_path: Path,
        list: bool,
        copy: bool,
        gitlab: bool,
        leaderboard: bool,
        list_commits: bool,
        type: str):
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

    working_repo_handler = RepoHandler(repo_path)

    # LET THE USER KNOW WHAT I'M ABOUT TO DO
    click.secho(f"Generating statistics for {project_name}", fg='green')

    # LOOK FOR FILES TO REFACTOR

    commit_hash = get_scan_args(stats_type)[0]
    regex = get_scan_args(stats_type)[1]
    exclude = ["spec.ts", "stories.ts", "md"]
    current_files = working_repo_handler.get_files_to_refactor(regex, exclude=exclude)
    baseline_files = working_repo_handler.get_baseline_file_paths(
        commit_hash, regex, exclude=exclude)
    codeowners = get_codeowners(repo_path)

    if leaderboard or list_commits:
        working_repo_handler.move_to_baseline_commit('develop', pull=True)
        commits = working_repo_handler.get_commits_since_hash(commit_hash)
        spinner = Halo(text="Inspecting commits...", spinner="dots")
        spinner.start()
        leaderboard_data = build_leaderboard_data(commits, regex)
        spinner.stop()

        if list_commits:
            # DISPLAY A LIST OF RELEVANT COMMITS
            commits = leaderboard_data[1]
            display_commits(commits)

        if leaderboard:
            # DISPLAY A LEADERBOARD
            authors = leaderboard_data[0]
            display_leaderboard(authors)

    # compare each file list and return a list of File status objects
    status_files = build_file_status_list(
        baseline_files, current_files)

    # DRAW A TIMELINE OF REFACTORS LEFT

    # plt.date_form('Y/m/d')
    # plt.clc()
    # plt.plotsize(100, 10)
    #
    # plt.plot(dates, refactors_left)
    #
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
