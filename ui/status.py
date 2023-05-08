import git


def is_staged(repo_path, file_path):
    repo = git.Repo(repo_path)

    return file_path in [item.a_path for item in repo.index.diff("HEAD")]


def is_modified(repo_path, file_path):
    repo = git.Repo(repo_path)

    return file_path in [item.a_path for item in repo.index.diff(None)]


def is_untracked(repo_path, file_path):
    repo = git.Repo(repo_path)

    return file_path in repo.untracked_files


def is_committed(repo_path, file_path):
    repo = git.Repo(repo_path)
    latest_commit = repo.head.commit
    committed_files = latest_commit.stats.files

    return file_path in committed_files


def get_status(repo_path, file_path):
    if is_untracked(repo_path, file_path):
        return "UNTRACKED"
    if is_committed(repo_path, file_path):
        return "COMMITTED"
    if is_modified(repo_path, file_path):
        return "MODIFIED"
    if is_staged(repo_path, file_path):
        return "STAGED"
