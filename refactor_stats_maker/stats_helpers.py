import re
from dataclasses import dataclass

import plotext as plt
import pyperclip
from codeowners import CodeOwners


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
        return self.path.replace('src/', '')

    def to_json(self):
        return {'name': self.name(), 'path': self.path}

    def __str__(self):
        return f'  {self.get_fixed_icon()} {self.get_simple_path()}'


"""
This function assumes that each filename in the codebase is unique

A more robust way of doing this would be to use git to track the files between
commits

"""


def build_file_status_list(before: list[str], after: list[str]) -> list[File]:
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
    raise Exception('Unable to create file from status')


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
        team = [t[1].replace('@', '') for t in owners]
        # strip src root folder
        file_path = file_path.replace('src/', '')
        # replace pedromcosta ownership with the file's root folder
        team = [t.replace('pedromcosta', file_path.split('/')[0]) for t in team]
    else:
        team = ['Orphaned files']

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

        if team_name.startswith('bs'):
            team_name = 'Buy&Sell'
        if team_name.startswith('cp'):
            team_name = 'Cross Platform'
        if team_name.startswith('iss'):
            team_name = 'Integrations'
        if team_name.startswith('mc'):
            team_name = 'Maintenance Core'
        if team_name.startswith('pedro'):
            team_name = 'Orphaned files'

        existing = report_data.get(team_name, [])

        report_data[team_name] = existing + [f.to_json() for f in files]

    return report_data


def build_report_data(files: list[File], codeowners, verbose=False,
                      format_for_gitlab=False
                      ) -> (str, [], [], []):
    team_names = []
    percentages = []

    report_lines = []

    assignments = assign_files_to_teams(files, codeowners)

    for team, files in sorted(assignments.items()):
        fixed_files_count = len([f for f in files if f.fixed])
        total_file_count = len(files)

        pct_done = round((fixed_files_count / total_file_count) * 100, 2)
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


"""
SHITIEST CODE EVER
"""


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
