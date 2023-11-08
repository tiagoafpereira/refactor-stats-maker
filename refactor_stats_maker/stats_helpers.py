import re
from dataclasses import dataclass

import plotext as plt
import pyperclip


@dataclass(order=True)
class File:
    path: str
    fixed: bool = False

    def name(self):
        return self.path.split("/")[-1]


def get_most_recent_file(file: File, recent_files: list[File]):
    return next((f for f in recent_files if f.name() == file.name()), file)


"""
SHITIEST CODE EVER
"""


def build_report_data(
        assignments,
        baselines={},
        verbose=False,
        format_for_gitlab=False,
) -> (str, [], [], []):
    team_names = []
    percentages = []

    baseline_file_counts = {k: len(v) for k, v in baselines.items()}
    baseline_files_per_team = {k: [File(path) for path in v] for k, v in
                               baselines.items()}
    file_status_list = {}

    report_lines = []

    for team, files_to_fix in sorted(assignments.items()):
        files_to_fix = [File(f) for f in files_to_fix]
        pending = len(files_to_fix)

        baseline = baseline_file_counts.get(team, 0)

        if baseline == 0:
            baseline = pending

        baseline_files: list[File] = baseline_files_per_team.get(team, [])
        baseline_files = sorted(baseline_files, key=lambda f: f.name())
        files_to_fix_names = [f.name() for f in files_to_fix]
        baseline_file_names = [f.name() for f in baseline_files]
        baseline_file_names = sorted(baseline_file_names)

        if baseline_files:
            file_items = [
                File(file.path, fixed=file.name() not in files_to_fix_names) for file in
                baseline_files
            ]
        else:
            file_items = [File(file, fixed=False) for file in
                          sorted(files_to_fix_names)]

        print(file_items)

        # add all files in files_to_fix NOT in baseline_files aka new files to refactor
        new_files = [f.path for f in files_to_fix if
                     f.name() not in baseline_file_names]
        new_files = list(set(new_files))
        new_files = [File(f) for f in new_files]

        for new_file in new_files:
            match = [f for f in file_items if f.name() == new_file.name()]
            if not match:
                file_items.append(File(new_file.path, new_file.fixed))

        file_items = sorted(file_items, key=lambda f: f.path)

        # replace each entry in file_items with the matching one on the most recent
        # changelist
        file_items = [get_most_recent_file(f, files_to_fix) for f in
                      file_items]

        fixed_files_count = len([f for f in file_items if f.fixed])
        total_file_count = len(list(file_items))

        pct_done = round(((fixed_files_count / total_file_count)) * 100, 0)
        percentages.append(pct_done)

        fixed_string = f"fixed {fixed_files_count} of {total_file_count} files"

        # Get the team name only
        result = re.search(r"@infraspeak/.*/(.*)/.*", team)
        if result:
            team_name = result.group(1)
        else:
            team_name = team
        team_names.append(f"{team_name} {fixed_files_count}/{total_file_count}")

        if verbose:
            percent_done_by_team = f"{pct_done}% DONE ({fixed_string})"
            report_lines.append(f"{team} {percent_done_by_team}")

            tab_character = "  "

            # if format_for_gitlab:
            #     tab_character = '&emsp;'

            for file_item in sorted(file_items):
                file_path = file_item.path
                if file_item.fixed:
                    report_lines.append(f"{tab_character}✅ {file_path}")
                    file_status_list[file_path] = True
                else:
                    report_lines.append(f"{tab_character}❌ {file_path}")
                    file_status_list[file_path] = False
        else:
            for file_item in sorted(file_items):
                file_path = file_item[0]
                if file_item[1]:
                    file_status_list[file_path] = False
                else:
                    file_status_list[file_path] = True

    # REPORT TEXT

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
    return report_text, file_status_list, team_names, percentages


def display_team_assignments(
        assignments,
        baselines={},
        verbose=False,
        format_for_gitlab=False,
        copy_to_clipboard=False,
):
    # PRINT FILES AND STATS

    report_data = build_report_data(
        assignments,
        baselines,
        verbose,
        format_for_gitlab,
    )

    report_text = report_data[0]
    file_status_list = report_data[1]
    team_names = report_data[2]
    percentages = report_data[3]

    # OVERALL STATS

    fixed_files_count = len([f for f in file_status_list.values() if f is True])
    total_file_count = len(list(file_status_list.items()))

    if total_file_count:
        percent_done = (fixed_files_count / total_file_count) * 100
    else:
        percent_done = 0

    title = f"OVERALL REFACTORING STATUS {percent_done:.2f}%"

    # BY TEAM STATS

    if not team_names:
        print("No stats to display")
        exit(0)

    plt.simple_bar(team_names, percentages, width=75, title=title)
    plt.show()

    # PRINT FILE LIST

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
