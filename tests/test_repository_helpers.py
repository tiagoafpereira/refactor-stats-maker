from pathlib import Path

from refactor_stats_maker.repository_helpers import RepoHandler


def test_get_files_to_refactor_in_folder():
    repo_path = Path('tests', 'test_repository')
    assert RepoHandler.get_files_to_refactor_in_folder(repo_path, "@Component") == [
        "src/views/works/ScreenWorks.vue"]
