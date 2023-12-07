from codeowners import CodeOwners

from refactor_stats_maker import stats_helpers
from refactor_stats_maker.stats_helpers import File


#
# FILE CLASS TESTS
#


def test_empty():
    file = File("some/path/name")
    assert file.path == "some/path/name"
    assert file.name() == "name"


#
# FILE STATUS TESTS
#

def test_index_files():
    assert stats_helpers.index_files(["some/path/to/file"]) == {
        "file": "some/path/to/file"}


def test_empty_file_status_list():
    assert stats_helpers.build_file_status_list([], []) == []


def test_fixed_file_status():
    file_a = "some/path/to/fileA"
    assert stats_helpers.build_file_status_list([file_a], []) == [
        File(file_a, fixed=True)
    ]


def test_not_fixed_file_status():
    file_a = "some/path/to/fileA"
    assert stats_helpers.build_file_status_list([file_a], [file_a]) == [
        File(file_a, fixed=False)
    ]


def test_not_fixed_new_file_status():
    file_a = "some/path/to/fileA"
    assert stats_helpers.build_file_status_list([], [file_a]) == [
        File(file_a, fixed=False, is_new=True)
    ]


def test_not_fixed_moved_file_status():
    file_before = "some/path/to/fileA"
    file_after = "some/other/path/to/fileA"
    assert stats_helpers.build_file_status_list([file_before], [file_after]) == [
        File(file_after, fixed=False)
    ]


# MULTIPLE FILES

def test_fixed_files_status():
    file_a = "some/path/to/fileA"
    file_b = "some/path/to/fileB"
    assert stats_helpers.build_file_status_list([file_a, file_b], []) == [
        File(file_a, fixed=True),
        File(file_b, fixed=True)
    ]


def test_one_fixed_and_one_new_failed_status():
    file_a = "some/path/to/fileA"
    file_b = "some/path/to/fileB"
    assert stats_helpers.build_file_status_list([file_a], [file_b]) == [
        File(file_a, fixed=True),
        File(file_b, fixed=False, is_new=True)
    ]


#
# FILE ASSIGNMENTS
#

def test_file_assignment_to_teams():
    codeowners = CodeOwners("^[Domain]\npathA/ @TeamA\npathB @TeamB")
    assert stats_helpers.assign_files_to_teams([
        File('pathA/fileA'),
        File('pathB/fileB')
    ], codeowners) == {
               'TeamA': [File(path='pathA/fileA', fixed=False, is_new=False)],
               'TeamB': [
                   File(path='pathB/fileB', fixed=False, is_new=False)]}


def test_orphaned_files_assignment():
    codeowners_txt = "^[Domain]\nsome/path/to/ @Team"
    assert stats_helpers.assign_files_to_teams([
        File('some/other/path/to/fileA')
    ], CodeOwners(codeowners_txt)) == {
               'Orphaned files': [File('some/other/path/to/fileA')]}


#
# FILE OWNERS
#

def test_file_without_owner():
    codeowners = CodeOwners("^[Domain]\npathA @Team")
    assert stats_helpers.get_file_owners('pathB',
                                         codeowners) == ['Orphaned files']


def test_file_with_owner():
    codeowners = CodeOwners("^[Domain]\npath @Team")
    assert stats_helpers.get_file_owners('path',
                                         codeowners) == ['Team']


def test_file_with_owners():
    codeowners = CodeOwners("^[Domain]\npath @TeamA @TeamB")
    assert stats_helpers.get_file_owners('path',
                                         codeowners) == ['TeamA', 'TeamB']


#
# REPORT DATA TESTS
#

def test_empty_report_data():
    codeowners = CodeOwners("")
    team_assignments = stats_helpers.build_report_data([], codeowners)
    assert team_assignments == ("", [], [], [])


def test_report_data_single_file_not_fixed():
    codeowners = CodeOwners("^[Domain]\nsome/path/to/ @team")
    files = [File("some/path/to/FileA")]
    team_assignments = stats_helpers.build_report_data(
        files, codeowners, verbose=True
    )
    assert team_assignments == (
        "team 0.0% DONE (fixed 0 of 1 files)\n  ❌ some/path/to/FileA",
        [File(path='some/path/to/FileA', fixed=False, is_new=False)],
        ["team 0/1"],
        [0.0],
    )


def test_report_data_single_file_fixed():
    codeowners = CodeOwners("^[Domain]\nsome/path/to/ @team")
    files = [File("some/path/to/FileA", fixed=True)]
    team_assignments = stats_helpers.build_report_data(
        files, codeowners, verbose=True
    )
    assert team_assignments == (
        "team 100.0% DONE (fixed 1 of 1 files)\n  ✅ some/path/to/FileA",
        [File(path='some/path/to/FileA', fixed=True, is_new=False)],
        ["team 1/1"],
        [100.0],
    )


#
# TEAM ASSIGNMENTS DISPLAY
#

def test_empty_team_assignments(capsys):
    status_files = []
    codeowners = CodeOwners("")
    stats_helpers.display_team_assignments("project name", status_files, codeowners)
    out, err = capsys.readouterr()
    assert out == 'No stats to display\n'


def test_single_file_assignment(capsys):
    status_files = [File('some/path/to/fileA', fixed=True)]
    status_files += [File('some/path/to/fileB', fixed=False)]
    codeowners = CodeOwners("^[Domain]\nsome/path @ATeam")
    stats_helpers.display_team_assignments("project name", status_files, codeowners)
    out, err = capsys.readouterr()
    assert out == (
        '\x1b[1m\x1b[38;5;7m──────────── OVERALL REFACTORING STATUS OF PROJECT NAME '
        '50.00% ────────────\x1b[0m\x1b[0m\n'
        '\x1b[1m\x1b[38;5;7mATeam 1/2\x1b[0m\x1b[0m '
        '\x1b['
        '38;5;12m▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇\x1b[0m '
        '\x1b[1m\x1b[38;5;7m50.00\x1b[0m\x1b[0m\n')
