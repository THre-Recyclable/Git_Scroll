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

    print('relPath:' + relative_path)

    print('untracked:')
    for item in repo.untracked_files:
        print(item)

    print('staged:')
    for item in repo.index.diff('HEAD'):
        print(item)
        print('a path: ' + item.a_path)

    # untracked check prior - the working directory would have untracked files.
    # because of the newly created file or 'git rm --cached'
    if relative_path in repo.untracked_files:
        return 'untracked'
    # if both modified and staged, modified should be prior.
    elif relative_path in [item.a_path for item in repo.index.diff(None)]:
        return 'modified'
    elif relative_path in [item.a_path for item in repo.index.diff('HEAD')]:
        return 'staged'

    # this part is needed because of .gitignore.
    # a file ignored by .gitignore doesn't appear in repo.untracked_files.
    # so we need to check if this is committed before.
    # if not, it is untracked.

    # we already checked modified and staged already.
    # we just need to check whether the file has been committed or not.
    try:
        latest_commit = next(repo.iter_commits(paths=relative_path, max_count=1))
        return 'committed'
    except StopIteration:
        return 'untracked'

