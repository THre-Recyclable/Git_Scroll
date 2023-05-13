import git
import os

status_cache = {}
mtime_cache = {}
calculated_cache = {}


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
        if os.path.exists(os.path.join(repo.working_tree_dir, file)):
            file_path = os.path.join(repo.working_tree_dir, file)
            file_path = file_path.replace('\\', '/')
            if get_status(file_path, False) == 'staged':
                status_cache[file_path] = 'committed'
                mtime = os.path.getmtime(file_path)
                mtime_cache[file_path] = mtime


def process_staged_directories(dirpath):
    repo = git.Repo(dirpath, search_parent_directories=True)
    for root, dirnames, filenames in os.walk(repo.working_tree_dir):
        for dirname in dirnames:
            path = os.path.join(root, dirname)
            path = path.replace('\\', '/')
            path += '/'

            if status_cache.get(path, 'unknown') == 'staged':
                status_cache[path] = 'committed'


def get_directory_status(dirpath):
    # print('path: ' + dirpath)
    dirpath = os.path.abspath(dirpath)
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


def get_file_status(filepath):
    filepath = filepath.replace('\\', '/')
    if status_cache.get(filepath, 'unknown') != 'unknown':
        return status_cache[filepath]

    return calculate_status(filepath)


def get_git_status(path):
    repo = git.Repo(path, search_parent_directories=True)
    repo_path = repo.working_tree_dir
    path = path.replace('\\', '/')
    if os.path.isdir(path):
        path += '/'

    # print('get_git_status path: ' + path)

    # print('getting cache in path: ' + path)
    if calculated_cache.get(repo_path, False) is True:
        file_status = status_cache.get(path, 'unknown')

        # cache key exists
        if file_status != 'unknown':
            # print('cache key exists...')
            # if it is file, check whether it is up-to-date
            if os.path.isfile(path) and mtime_cache[path] == os.path.getmtime(path):
                # print('recoreded mtime: ' + str(mtime_cache[path]))
                # print('actual mtime: ' + str(os.path.getmtime(path)))
                # print('returning cache...')
                return file_status
            elif os.path.isdir(path):
                return file_status

        # cache key exists but is not up-to-date, re-calculate needed
        if file_status != 'unknown' and mtime_cache[path] != os.path.getmtime(path):
            # print('re-calculate needed...')
            file_status = calculate_status(path)
            if file_status == 'committed':
                status_cache[path] = 'committed'
                if os.path.isfile(path):
                    mtime_cache[path] = os.path.getmtime(path)

            return file_status

        # if there is no such cache key (maybe in subdirectory of untracked or ignored directory or committed.
        # or just newly created file)
        # print('no cache key found...')
        if os.path.isdir(path):
            path = os.path.dirname(path)
        parent_dir = os.path.dirname(path) + '/'

        # check parent directory status
        # print('checking parent directory status...')
        if os.path.isdir(path):
            path += '/'
        # print('path: ' + path)
        # print('parent_dir: ' + parent_dir)
        parent_status = status_cache.get(parent_dir, 'unknown')
        if parent_status == 'untracked':
            status_cache[path] = 'untracked'
            if os.path.isfile(path):
                mtime_cache[path] = os.path.getmtime(path)
            return 'untracked'
        elif parent_status == 'ignored':
            status_cache[path] = 'ignored'
            if os.path.isfile(path):
                mtime_cache[path] = os.path.getmtime(path)
            return 'ignored'
        # if the file is not in untracked or ignored directory
        # committed or newly created file
        else:
            # print('not in U/I directory, re-calculate needed...')
            file_status = calculate_status(path)
            if file_status == 'committed':
                status_cache[path] = 'committed'
                if os.path.isfile(path):
                    mtime_cache[path] = os.path.getmtime(path)

            return file_status
    #         file_status = status_cache.get(path, 'unknown')
    #         if file_status == 'unknown':
    #             return calculate_status(path)
    #         else:
    #             return file_status
    #
    # # print('cache failed: ' + path)
    # # if the cache wasn't calculated yet
    # return calculate_status(path)
    # print('initial calculating')
    return calculate_status(path)


def calculate_status(path):
    # print('starting calculating...')
    repo = git.Repo(path, search_parent_directories=True)
    root_dir = repo.working_tree_dir
    calculated_cache[root_dir] = True
    root_dir = root_dir.replace('\\', '/')
    status_output = repo.git.execute(['git', 'status', '--porcelain', '--ignored']).splitlines()

    # print('calculate_status: ' + path)
    origin_path = path

    # initialize cache info
    # print('initializing...')
    for root, dirs, files in os.walk(repo.working_tree_dir):
        if '.git' in dirs:
            dirs.remove('.git')

        for dirname in dirs:
            # print('dir name: ' + dirname)
            path = os.path.join(root, dirname)
            path = path.replace('\\', '/')
            mtime = os.path.getmtime(path)
            path += '/'
            # print('init path: ' + path)

            status_cache[path] = 'committed'
            if mtime_cache.get(path, '-1') == '-1':
                mtime_cache[path] = mtime

        for filename in files:
            # print('file name: ' + filename)
            path = os.path.join(root, filename)
            path = path.replace('\\', '/')
            mtime = os.path.getmtime(path)
            # print('init path: ' + path)

            status_cache[path] = 'committed'
            if mtime_cache.get(path, '-1') == '-1':
                mtime_cache[path] = mtime
    # print('starting parsing...')

    for line in status_output:
        status, filepath = line[:2], line[3:]
        if '->' in filepath:
            _, filepath = filepath.split(' -> ')
        filepath = os.path.join(root_dir, filepath)
        filepath = filepath.replace('\\', '/')
        if os.path.isdir(filepath):
            isdir = True
        else:
            isdir = False
        # print('now processing: ' + filepath)
        # print('entire path: ' + filepath)
        # print('status:' + status)
        if status == '??':
            status_cache[filepath] = 'untracked'
            # print('setting untracked')
            if isdir is True:
                change_all(os.path.dirname(filepath), 'untracked')
        elif status == '!!':
            status_cache[filepath] = 'ignored'
            # print('setting ignored')
            if isdir is True:
                change_all(os.path.dirname(filepath), 'ignored')
        elif status[1] != ' ':
            # print('setting modified')
            status_cache[filepath] = 'modified'
        elif status in ['A ', 'R ', 'D ', 'M ', 'C ', 'U ']:
            # print('setting staged')
            status_cache[filepath] = 'staged'

        if os.path.isfile(filepath):
            mtime_cache[filepath] = os.path.getmtime(filepath)

        # print('setting dir status...')
        file_status = status_cache[filepath]
        if os.path.isdir(filepath):
            filepath = os.path.dirname(filepath)
        parent_dir = os.path.dirname(filepath)
        # print('dir path: ' + parent_dir)
        # print('root path: ' + root_dir)
        while parent_dir != root_dir and file_status != 'ignored':
            # print('now checking: ' + parent_dir)
            # if status_cache.get(parent_dir + '/', 'unknown') == 'unknown':
                # status_cache[parent_dir + '/'] = 'committed'

            # print('checking cache at:' + parent_dir+'/')
            if status_cache[parent_dir + '/'] == 'untracked':
                break
            elif status_cache[parent_dir + '/'] == 'modified' and file_status != 'untracked':
                break
            elif status_cache[parent_dir + '/'] == 'staged' and file_status not in ['untracked', 'modified']:
                break
            else:
                # print('setting status: ' + file_status)
                status_cache[parent_dir + '/'] = file_status
            # print('moving upper directory...')
            parent_dir = os.path.dirname(parent_dir)
            # print('now directory is: ' + parent_dir)
            # print('now root is: ' + root_dir)

        # print('moving to next file...')

    # print('directory status checking ended')

    # print('checking if working tree clean...')
    # if len(list(status_cache.keys())) == 0:
    #     return 'committed'

    # print('dirpath: ' + path)
    # print('value: ' + status_cache[path])
    # print('finished setting dir status...')
    # print('returning status: ' + status_cache.get(origin_path, 'root'))
    # print('target address: ' + origin_path)
    return status_cache.get(origin_path, 'root')


def change_all(dirpath, status):
    for root, dirs, files in os.walk(dirpath):
        for dir in dirs:
            path = os.path.join(root, dir)
            path = path.replace('\\', '/')
            mtime = os.path.getmtime(path)
            path += '/'

            status_cache[path] = status
            mtime_cache[path] = mtime

        for file in files:
            path = os.path.join(root, file)
            path = path.replace('\\', '/')
            mtime = os.path.getmtime(path)

            status_cache[path] = status
            mtime_cache[path] = mtime
