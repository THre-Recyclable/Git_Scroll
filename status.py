import git
import os


def is_git_repository(path):
    try:
        _ = git.Repo(path, search_parent_directories=True)
        return True
    except git.exc.InvalidGitRepositoryError:
        return False


def get_status(file_path):
    repo = git.Repo(file_path, search_parent_directories=True)
    relative_path = os.path.relpath(file_path, repo.working_tree_dir)

    if relative_path in repo.untracked_files:
        file_status = 'untracked'
    else:
        index_diff = repo.index.diff(None)
        head_diff = repo.index.diff('HEAD')

        if any(item.b_path == relative_path for item in index_diff):
            file_status = 'modified'
        elif any(item.b_path == relative_path for item in head_diff):
            file_status = 'staged'
        else:
            file_status = 'committed'

    return file_status
