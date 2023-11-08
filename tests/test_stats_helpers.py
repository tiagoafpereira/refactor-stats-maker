from refactor_stats_maker import stats_helpers

from refactor_stats_maker.stats_helpers import File


#
# FILE CLASS TESTS
#


def test_empty():
    file = File("some/path/name")
    assert file.path == "some/path/name"
    assert file.name() == "name"


def test_empty_report_data():
    team_assignments = stats_helpers.build_report_data({}, {})
    assert team_assignments == ("", {}, [], [])


def test_report_data_single_file_not_fixed():
    assignments = {"team": ["FileA"]}
    baseline = {"team": ["FileA"]}
    team_assignments = stats_helpers.build_report_data(
        assignments, baseline, verbose=True
    )
    assert team_assignments == (
        "team 0.0% DONE (fixed 0 of 1 files)\n  ❌ FileA",
        {"FileA": False},
        ["team 0/1"],
        [0.0],
    )


def test_report_data_single_file_fixed():
    assignments = {"team": []}
    baseline = {"team": ["FileA"]}
    team_assignments = stats_helpers.build_report_data(
        assignments, baseline, verbose=True
    )
    assert team_assignments == (
        "team 100.0% DONE (fixed 1 of 1 files)\n  ✅ FileA",
        {"FileA": True},
        ["team 1/1"],
        [100.0],
    )


def test_report_data_single_file_not_in_baseline():
    assignments = {"team": ["FileA"]}
    baseline = {"team": []}
    team_assignments = stats_helpers.build_report_data(
        assignments, baseline, verbose=True
    )
    assert team_assignments == (
        "team 0.0% DONE (fixed 0 of 1 files)\n  ❌ FileA",
        {"FileA": False},
        ["team 0/1"],
        [0.0],
    )


def test_report_data_one_new_one_fixed():
    assignments = {"team": ["FileA"]}
    baseline = {"team": ["FileB"]}
    team_assignments = stats_helpers.build_report_data(
        assignments, baseline, verbose=True
    )
    assert team_assignments == (
        "team 50.0% DONE (fixed 1 of 2 files)\n  ❌ FileA\n  ✅ FileB",
        {"FileA": False, "FileB": True},
        ["team 1/2"],
        [50.0],
    )


def test_report_data_file_moved():
    assignments = {"team": ["pathB/FileA"]}
    baseline = {"team": ["pathA/FileA"]}
    team_assignments = stats_helpers.build_report_data(
        assignments, baseline, verbose=True
    )
    assert team_assignments == (
        "team 0.0% DONE (fixed 0 of 1 files)\n  ❌ pathB/FileA",
        {"pathB/FileA": False},
        ["team 0/1"],
        [0.0],
    )
