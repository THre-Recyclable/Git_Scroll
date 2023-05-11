import git
import os

status_cache = {}


def is_git_repository(path):
    try:
        _ = git.Repo(path, search_parent_directories=True)
        return True
    except git.exc.InvalidGitRepositoryError:
        return False


def get_status(file_path, get_status_again):
    repo = git.Repo(file_path, search_parent_directories=True)
    relative_path = os.path.relpath(file_path, repo.working_tree_dir)
    # this is needed, because git uses '/' for directories but windows uses '\' for directories.
    relative_path = relative_path.replace('\\', '/')

    # executing every code below is inefficient, so we will use simple nested dictionary.
    repo_cache = status_cache.get(repo.working_tree_dir, {})
    if relative_path in repo_cache and get_status_again is False:
        return repo_cache[relative_path]

    # untracked check prior - the working directory would have untracked files.
    # because of the newly created file or 'git rm --cached'
    if relative_path in repo.untracked_files:
        repo_cache[relative_path] = 'untracked'
        return 'untracked'
    # if both modified and staged, modified should be prior.
    if relative_path in [item.a_path for item in repo.index.diff(None)]:
        repo_cache[relative_path] = 'modified'
        return 'modified'

    # if it doesn't have any commit object, there is no diff('HEAD')
    # in this case, unfortunately, we need to check every file in staging area.
    # fortunately, we don't have committed state here.
    if len(list(repo.branches)) == 0:
        staged_files = [item[0] for item in repo.index.entries]
        if relative_path in staged_files:
            repo_cache[relative_path] = 'staged'
            return 'staged'
        else:
            repo_cache[relative_path] = 'untracked'
            return 'untracked'

    if relative_path in [item.a_path for item in repo.index.diff('HEAD')]:
        repo_cache[relative_path] = 'staged'
        return 'staged'

    # this part is needed because of .gitignore.
    # a file ignored by .gitignore doesn't appear in repo.untracked_files.
    # so we need to check if this is committed before.
    # if not, it is untracked.

    # we already checked modified and staged already.
    # we just need to check whether the file has been committed or not.
    try:
        latest_commit = next(repo.iter_commits(paths=relative_path, max_count=1))
        repo_cache[relative_path] = 'committed'
        return 'committed'
    except StopIteration:
        repo_cache[relative_path] = 'untracked'
        return 'untracked'
