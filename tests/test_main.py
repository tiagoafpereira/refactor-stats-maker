from codeowners import CodeOwners

import refactor_stats_maker.__main__


def test_get_team_assignments_file_without_team():
    codeowners = CodeOwners("^[Domain]\npath")
    assignments = refactor_stats_maker.__main__.get_team_assignments(['path/fileA'],
                                                                     codeowners)
    assert assignments == {'Orphaned files': ['path/fileA']}


def test_get_team_assignments_file_with_team():
    codeowners = CodeOwners("^[Domain]\npath @Team")
    assignments = refactor_stats_maker.__main__.get_team_assignments(['path/fileA'],
                                                                     codeowners)
    assert assignments == {'Team': ['path/fileA']}


def test_get_team_assignments_file_owned_by_pedromcosta():
    codeowners = CodeOwners("^[Domain]\nsrc/path @pedromcosta")
    assignments = refactor_stats_maker.__main__.get_team_assignments(
        ['src/path/fileA'],
        codeowners)
    assert assignments == {'path': ['src/path/fileA']}
