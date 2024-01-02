import re
import time
from abc import ABC
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from itertools import chain

import holidays
import humanize
import numpy as np
import plotext as plt
import pyperclip
from codeowners import CodeOwners
from git import Commit, Actor
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text


@dataclass(order=True)
class File:
    path: str
    fixed: bool = False
    is_new: bool = False

    def name(self):
        return self.path.split("/")[-1]

    def get_fixed_icon(self) -> str:
        if self.fixed:
            return "✅"
        else:
            return "❌"

    def get_simple_path(self):
        return self.path.replace("src/", "")

    def to_json(self):
        return {"name": self.name(), "path": self.path}

    def __str__(self):
        return f"  {self.get_fixed_icon()} {self.get_simple_path()}"


@dataclass(order=True)
class RefactorCommit:
    hexsha: str
    date: datetime
    summary: str
    author_name: str
    author_email: str
    refactor_count: int
    remaining_files_count: int

    def __str__(self):
        return f"{self.summary} {self.refactor_count} {self.remaining_files_count}"


@dataclass
class ConclusionEstimates:
    start_date: datetime
    end_date: datetime
    last_refactor_date: datetime
    files_remaining: int
    files_refactored: int
    workdays_since_start: int
    refactored_files_per_workday: float
    estimated_end_date: datetime
    estimated_days_left: int


def build_file_status_list(before: list[str], after: list[str]) -> list[File]:
    """
    This function assumes that each filename in the codebase is unique

    A more robust way of doing this would be to use git to track the files between
    commits

    """
    # index each file by its filename

    before_files_list = index_files(before)
    after_files_list = index_files(after)
    index = {}
    file_list = []

    # iterate files from the oldest snapshot
    for key, before_value in before_files_list.items():
        after_value = after_files_list.get(key)
        index[key] = (before_value, after_value)

    # iterate files from the most recent snapshot
    for key, after_value in after_files_list.items():
        current_value = index.get(key)
        if current_value:
            current_value = (before_files_list.get(key), after_value)
        else:
            current_value = (None, after_value)
        index[key] = current_value

    # map each tuple in index to a File
    for k, v in index.items():
        file_list.append(build_file_status(v))

    return file_list


"""
Takes a tuple of file paths and creates a File
"""


def build_file_status(status: tuple) -> File:
    match status:
        case (path, None):
            return File(path, fixed=True)
        case (None, path):
            return File(path, fixed=False, is_new=True)
        case (_, path):
            return File(path, fixed=False)
    raise Exception("Unable to create file from status")


def index_files(files: list[str]) -> dict[str, str]:
    index = {}
    for f in files:
        index[f.split("/")[-1]] = f
    return index


def get_most_recent_file(file: File, recent_files: list[File]):
    return next((f for f in recent_files if f.name() == file.name()), file)


def assign_files_to_teams(files: list[File], codeowners: CodeOwners):
    index = {}

    for f in files:
        teams = get_file_owners(f.path, codeowners)
        for team in teams:
            file_list = index.get(team, [])
            file_list.append(f)
            file_list = sorted(file_list, key=lambda x: x.path)
            index[team] = file_list

    return index


def get_file_owners(file_path: str, codeowners: CodeOwners) -> list[str]:
    owners = codeowners.of(file_path)
    if owners:
        team = [t[1].replace("@", "") for t in owners]
        # strip src root folder
        file_path = file_path.replace("src/", "")
        # replace pedromcosta ownership with the file's root folder
        team = [t.replace("pedromcosta", file_path.split("/")[0]) for t in team]
    else:
        team = ["Orphaned files"]

    return team


def export_report_data_to_json(files: list[File], codeowners):
    report_data = {}

    assignments = assign_files_to_teams(files, codeowners)

    for team, files in sorted(assignments.items()):
        # Get the team name only
        result = re.search(r"infraspeak/.*/(.*)/.*", team)
        if result:
            team_name = result.group(1)
        else:
            team_name = team

        if team_name.startswith("bs"):
            team_name = "Buy&Sell"
        if team_name.startswith("cp"):
            team_name = "Cross Platform"
        if team_name.startswith("iss"):
            team_name = "Integrations"
        if team_name.startswith("mc"):
            team_name = "Maintenance Core"
        if team_name.startswith("pedro"):
            team_name = "Orphaned files"

        existing = report_data.get(team_name, [])

        report_data[team_name] = existing + [f.to_json() for f in files]

    return report_data


def build_report_data(
    files: list[File], codeowners, verbose=False, format_for_gitlab=False
) -> (str, [], [], []):
    team_names = []
    percentages = []

    report_lines = []

    assignments = assign_files_to_teams(files, codeowners)

    for team, files in sorted(assignments.items()):
        fixed_files_count = len([f for f in files if f.fixed])
        total_file_count = len(files)

        pct_done = round((fixed_files_count / total_file_count) * 100, 1)
        percentages.append(pct_done)

        fixed_string = f"fixed {fixed_files_count} of {total_file_count} files"

        # Get the team name only
        result = re.search(r"infraspeak/.*/(.*)/.*", team)
        if result:
            team_name = result.group(1)
        else:
            team_name = team
        team_names.append(f"{team_name} {fixed_files_count}/{total_file_count}")

        if verbose:
            percent_done_by_team = f"{pct_done}% DONE ({fixed_string})"
            report_lines.append(f"{team_name} {percent_done_by_team}")

            for file in files:
                report_lines.append(str(file))

    # REPORT TEXT

    if report_lines:
        report_text = "\n".join(report_lines)

        if format_for_gitlab:
            report_text = f"""
    <p>
    <details>
    <summary>Click for detailed file list</summary>
    <pre>
    {report_text}
    </pre>
    </details>
    </p>
            """
    else:
        report_text = ""

    return report_text, files, team_names, percentages


def display_team_assignments(
    project_name: str,
    status_files: list[File],
    codeowners: CodeOwners,
    verbose=False,
    format_for_gitlab=False,
    copy_to_clipboard=False,
):
    # report_data = export_report_data_to_json(status_files, codeowners)
    # json.dump(report_data, open('refactors.json', 'w'), sort_keys=True, indent=4)
    # create_jira_issues(status_files, codeowners)

    # PRINT FILES AND STATS

    report_data = build_report_data(
        status_files,
        codeowners,
        verbose,
        format_for_gitlab,
    )

    report_text = report_data[0]
    team_names = report_data[2]
    percentages = report_data[3]

    # OVERALL STATS

    fixed_files_count = len([f for f in status_files if f.fixed])
    total_file_count = len(status_files)

    if total_file_count:
        percent_done = (fixed_files_count / total_file_count) * 100
    else:
        percent_done = 0

    title = f"OVERALL REFACTORING STATUS OF {project_name.upper()} {percent_done:.2f}%"

    # BY TEAM STATS

    if not team_names:
        print("No stats to display")
        return

    plt.simple_bar(team_names, percentages, width=75, title=title)
    plt.show()

    # PRINT FILE LIST

    if report_text:
        print()

        print(report_text)

    if copy_to_clipboard:
        if format_for_gitlab:
            # strip ANSI color escape codes from string before copying to clipboard
            text_plot = str(f"<pre>{plt.uncolorize(plt.build())}</pre>")
        else:
            text_plot = str(f"{plt.uncolorize(plt.build())}\n")
        report_text = text_plot + report_text
        pyperclip.copy(report_text)


def build_stats_data(
    commits: list[Commit], regex: str, baseline_file_list: list[str]
) -> list[RefactorCommit]:
    regex_expr = re.compile(regex)

    # GET REFACTORS LEFT PER COMMIT
    refactor_commits: dict[str, RefactorCommit] = {}

    for commit in list(reversed(commits)):
        diff = commit.diff(commit.parents)

        # look at modified M and deleted D files to check for applied refactors
        for d in chain(diff.iter_change_type("M"), diff.iter_change_type("D")):
            # ignore files that we know won't have any refactors applied
            if not d.a_path.endswith("vue") and not d.a_path.endswith("ts"):
                continue

            before_text = ""
            after_text = d.a_blob.data_stream.read().decode()
            deleted_matches = 0
            deleted_file = False
            try:
                before_text = d.b_blob.data_stream.read().decode()
                # this throws if the file was deleted
                # still don't know WHY since it's the _before_ blob that fails to be
                # decoded...
            except AttributeError:
                deleted_matches = len(regex_expr.findall(after_text))
                deleted_file = True
            matches_before = len(regex_expr.findall(before_text))
            matches_after = len(regex_expr.findall(after_text))

            diff_matches = matches_before - matches_after
            refactor_commit = refactor_commits.get(
                commit.hexsha,
                RefactorCommit(
                    commit.hexsha,
                    datetime.fromtimestamp(commit.committed_date),
                    commit.summary,
                    commit.author.name,
                    commit.author.email,
                    0,
                    len(baseline_file_list),
                ),
            )
            if diff_matches > 0:
                refactor_commit.refactor_count = (
                    refactor_commit.refactor_count + diff_matches + deleted_matches
                )
            if matches_before > 0 and (matches_after == 0 or deleted_file):
                if d.a_path in baseline_file_list:
                    baseline_file_list.remove(d.a_path)
                    refactor_commit.remaining_files_count = len(baseline_file_list)

            if refactor_commit.refactor_count:
                refactor_commits[commit.hexsha] = refactor_commit

    return list(refactor_commits.values())


def build_leaderboard_data(commits: list[RefactorCommit]) -> dict[Actor, int]:
    leaderboard_data: dict[(str, str), int] = {}
    for commit in commits:
        refactor_count = leaderboard_data.get(
            (commit.author_name, commit.author_email), 0
        )
        refactor_count += commit.refactor_count
        leaderboard_data[(commit.author_name, commit.author_email)] = refactor_count
    return {Actor(k[0], k[1]): v for k, v in leaderboard_data.items()}


def build_chart_data(refactor_commits: list[RefactorCommit]) -> (dict)[datetime, int]:
    """

    :param refactor_commits: list of commits that contributed to the refactor effort
    :return: dictionary of refactored file count per datetime
    """
    refactors_by_date: dict[datetime, int] = {}
    for commit in refactor_commits:
        remaining_files = commit.remaining_files_count
        date_value = commit.date
        acc_refactors = min(
            refactors_by_date.get(date_value, remaining_files), remaining_files
        )
        refactors_by_date[date_value] = acc_refactors

    return refactors_by_date


class Oracle(ABC):
    @staticmethod
    def display_estimates(estimates: ConclusionEstimates):
        pretty_start_date = humanize.naturaldate(estimates.start_date)
        pretty_end_date = humanize.naturaldate(estimates.end_date)
        pretty_estimated_end_date = humanize.naturaldate(estimates.estimated_end_date)
        console = Console()
        text = Text()
        text.append("CURRENT STATUS\n", style="bold blue")
        text.append(
            f"Refactored {estimates.files_refactored} files over "
            f"{estimates.workdays_since_start} work days "
            f"between {pretty_start_date} and {pretty_end_date} (an "
            f"average of "
            f"{estimates.refactored_files_per_workday:.2f} refactored files per day)\n"
        )
        text.append("CONCLUSION ESTIMATE\n", style="bold blue")
        text.append(
            f"Ending on {pretty_estimated_end_date}: {estimates.estimated_days_left} days "
            f"left to refactor {estimates.files_remaining} files\n\n"
        )

        console.print(text)

    @staticmethod
    def make_prediction(refactors_by_date: dict[datetime, int]) -> ConclusionEstimates:
        raise NotImplementedError()


class BasicOracle(Oracle):
    @staticmethod
    def make_prediction(refactors_by_date: dict[datetime, int]) -> ConclusionEstimates:
        """
        This function calculates a very naive estimate based on the average number of
        refactored files per workday and uses that to determine the conclusion date.

        It does take holidays into account!

        :return: ConclusionEstimates
        :param refactors_by_date: a dictionary of refactored file count per datetime
        """
        first_day = list(refactors_by_date.keys())[0]
        last_day = datetime.today()
        # get holidays for Porto district
        local_holidays = list(
            holidays.country_holidays(
                "PT", subdiv="14", years=[first_day.year, last_day.year]
            ).keys()
        )
        days_delta = np.busday_count(
            first_day.date(), last_day.date(), holidays=local_holidays
        )

        if not days_delta:
            print("Unable to estimate end date: date range is empty")
            exit(1)

        refactors = list(refactors_by_date.values())
        first_refactor_count = refactors[0]
        last_refactor_count = refactors[-1]
        refactors_delta = first_refactor_count - last_refactor_count
        refactored_files_per_day: float = float(refactors_delta / days_delta)
        days_left = round(last_refactor_count / refactored_files_per_day)
        work_days_left = np.busday_count(
            last_day.date(), (last_day + timedelta(days=days_left)).date()
        )
        estimated_end_date = last_day + timedelta(days=float(work_days_left))

        return ConclusionEstimates(
            start_date=first_day,
            end_date=last_day,
            last_refactor_date=list(refactors_by_date.keys())[1],
            files_refactored=refactors_delta,
            files_remaining=last_refactor_count,
            workdays_since_start=int(days_delta),
            refactored_files_per_workday=refactored_files_per_day,
            estimated_end_date=estimated_end_date,
            estimated_days_left=days_left,
        )


def display_commits(commits: list[RefactorCommit]):
    table = Table(title="Commits in reverse chronological order", box=box.SIMPLE_HEAD)

    table.add_column("Author", style="#1FB0FF", justify="right")
    table.add_column("Date")
    table.add_column("Summary")

    for commit in commits:
        table.add_row(
            commit.author_name,
            time.strftime("%a, %d %b %Y %H:%M", time.gmtime(commit.date.timestamp())),
            commit.summary,
        )

    console = Console()
    console.print(table)
    return


def display_chart(remaining_refactors_by_date: dict[datetime, int]):
    plt.date_form("Y/m/d")
    plt.clc()
    plt.plotsize(100, 10)

    points = {k.strftime("%Y/%m/%d"): v for k, v in remaining_refactors_by_date.items()}

    plt.plot(points.keys(), points.values())

    plt.title("Refactored files over time")
    plt.xlabel("Date")
    plt.ylabel("Refactors left")
    plt.show()
    return ""


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
