import git
import os

status_cache = {}
mtime_cache = {}


def is_git_repository(path):
    try:
        repo = git.Repo(path, search_parent_directories=True)
        return True
    except git.exc.InvalidGitRepositoryError:
        return False


def is_root(path):
    repo = git.Repo(path, search_parent_directories=True)
    if os.path.abspath(path) == repo.working_tree_dir:
        return True
    else:
        return False


def get_status(file_path, get_status_again):
    # executing every code below is inefficient, so we will use simple nested dictionary.
    file_path = file_path.replace('\\', '/')
    file_status = status_cache.get(file_path, 'unknown')
    mtime = os.path.getmtime(file_path)
    if file_status != 'unknown' and get_status_again is False:
        # check if the file is modified
        if mtime_cache[file_path] == mtime:
            return file_status

    repo = git.Repo(file_path, search_parent_directories=True)
    relative_path = os.path.relpath(file_path, repo.working_tree_dir)
    # this is needed, because git uses '/' for directories but windows uses '\' for directories.
    relative_path = relative_path.replace('\\', '/')

    # untracked check prior - the working directory would have untracked files.
    # because of the newly created file or 'git rm --cached'
    if relative_path in repo.untracked_files:
        status_cache[file_path] = 'untracked'
        mtime_cache[file_path] = mtime
        return 'untracked'
    # if both modified and staged, modified should be prior.
    if relative_path in [item.a_path for item in repo.index.diff(None)]:
        status_cache[file_path] = 'modified'
        mtime_cache[file_path] = mtime
        return 'modified'

    # if it doesn't have any commit object, there is no diff('HEAD')
    # in this case, unfortunately, we need to check every file in staging area.
    # fortunately, we don't have committed state here.
    if len(list(repo.branches)) == 0:
        staged_files = [item[0] for item in repo.index.entries]
        if relative_path in staged_files:
            status_cache[file_path] = 'staged'
            mtime_cache[file_path] = mtime
            return 'staged'
        else:
            status_cache[file_path] = 'untracked'
            mtime_cache[file_path] = mtime
            return 'untracked'

    if relative_path in [item.a_path for item in repo.index.diff('HEAD')]:
        status_cache[file_path] = 'staged'
        mtime_cache[file_path] = mtime
        return 'staged'

    # this part is needed because of .gitignore.
    # a file ignored by .gitignore doesn't appear in repo.untracked_files.
    # so we need to check if this is committed before.
    # if not, it is untracked.

    # we already checked modified and staged already.
    # we just need to check whether the file has been committed or not.
    try:
        latest_commit = next(repo.iter_commits(paths=relative_path, max_count=1))
        status_cache[file_path] = 'committed'
        mtime_cache[file_path] = mtime
        return 'committed'
    except StopIteration:
        status_cache[file_path] = 'untracked'
        mtime_cache[file_path] = mtime
        return 'untracked'


def process_staged_files(dirpath, staged_files):
    repo = git.Repo(dirpath, search_parent_directories=True)
    for file in staged_files:
        file_path = os.path.join(repo.working_tree_dir, file)
        file_path = file_path.replace('\\', '/')
        if get_status(file_path, False) == 'staged':
            status_cache[file_path] = 'committed'
            mtime = os.path.getmtime(file_path)
            mtime_cache[file_path] = mtime


def get_directory_status(dirpath):
    # print('path: ' + dirpath)\
    dirpath = dirpath.replace('\\', '/')
    dirstate = status_cache.get(dirpath, 'unknown')
    mtime = os.path.getmtime(dirpath)
    if dirstate != 'unknown' and mtime_cache[dirpath] == mtime:
        return dirstate

    repo = git.Repo(dirpath, search_parent_directories=True)

    num_modified = 0
    num_staged = 0

    # Walk through the directory
    for dirpath, dirnames, filenames in os.walk(dirpath):
        for dirname in dirnames:
            subpath = os.path.join(dirpath, dirname)
            substate = get_directory_status(subpath)

            if substate == 'untracked':
                status_cache[dirpath] = 'untracked'
                mtime_cache[dirpath] = mtime
                return 'untracked'

            elif substate == 'modified':
                num_modified += 1

            elif substate == 'staged':
                num_staged += 1

        for filename in filenames:
            # Get absolute path of the file
            filepath = os.path.join(dirpath, filename)
            filestate = get_status(filepath, False)

            if filename in repo.untracked_files:
                status_cache[dirpath] = 'untracked'
                mtime_cache[dirpath] = mtime
                return 'untracked'

            elif filestate == 'modified':
                num_modified += 1

            elif filestate == 'staged':
                num_staged += 1

    if num_modified > 0:
        status_cache[dirpath] = 'modified'
        mtime_cache[dirpath] = mtime
        return 'modified'

    if num_staged > 0:
        status_cache[dirpath] = 'staged'
        mtime_cache[dirpath] = mtime
        return 'staged'

    status_cache[dirpath] = 'committed'
    mtime_cache[dirpath] = mtime
    return 'committed'
