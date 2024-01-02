import datetime

import time_machine
from codeowners import CodeOwners
from git import Actor

import refactor_stats_maker.__main__


def test_get_team_assignments_file_without_team():
    codeowners = CodeOwners("^[Domain]\npath")
    assignments = refactor_stats_maker.__main__.get_team_assignments(
        ["path/fileA"], codeowners
    )
    assert assignments == {"Orphaned files": ["path/fileA"]}


def test_get_team_assignments_file_with_team():
    codeowners = CodeOwners("^[Domain]\npath @Team")
    assignments = refactor_stats_maker.__main__.get_team_assignments(
        ["path/fileA"], codeowners
    )
    assert assignments == {"Team": ["path/fileA"]}


def test_get_team_assignments_file_owned_by_pedromcosta():
    codeowners = CodeOwners("^[Domain]\nsrc/path @pedromcosta")
    assignments = refactor_stats_maker.__main__.get_team_assignments(
        ["src/path/fileA"], codeowners
    )
    assert assignments == {"path": ["src/path/fileA"]}


def test_display_leaderboard(capsys):
    authors = {
        Actor("Jane", "jane@enterprise.com"): 10,
        Actor("John", "john@enterprise.com"): 1,
    }

    with time_machine.travel(datetime.date(2020, 3, 14)):
        refactor_stats_maker.__main__.display_leaderboard(authors)
        out, err = capsys.readouterr()
        assert out == (
            "        LEADERBOARD        \n"
            "┏━━━━━━━━┳━━━━━━━━━━━━━━━━┓\n"
            "┃ Author ┃ Refactor count ┃\n"
            "┡━━━━━━━━╇━━━━━━━━━━━━━━━━┩\n"
            "│   Jane │ 10             │\n"
            "│   John │ 1              │\n"
            "└────────┴────────────────┘\n"
        )

    with time_machine.travel(datetime.date(2020, 12, 24)):
        refactor_stats_maker.__main__.display_leaderboard(authors)
        out, err = capsys.readouterr()
        assert out == (
            "     🎄 LEADERBOARD 🎅      \n"
            "┏━━━━━━━━━┳━━━━━━━━━━━━━━━━┓\n"
            "┃  Author ┃ Refactor count ┃\n"
            "┡━━━━━━━━━╇━━━━━━━━━━━━━━━━┩\n"
            "│ 🎁 Jane │ 10             │\n"
            "│    John │ 1              │\n"
            "└─────────┴────────────────┘\n"
        )
