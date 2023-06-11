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


def process_staged_files(dirpath, staged_files):
    repo = git.Repo(dirpath, search_parent_directories=True)
    for file in staged_files:
        if os.path.exists(os.path.join(repo.working_tree_dir, file)):
            file_path = os.path.join(repo.working_tree_dir, file)
            file_path = file_path.replace('\\', '/')
            file_path = file_path.replace('"', '')
            if status_cache.get(file_path, 'unknown') == 'staged':
                status_cache[file_path] = 'committed'
                mtime = os.path.getmtime(file_path)
                mtime_cache[file_path] = mtime


def process_staged_directories(dirpath):
    repo = git.Repo(dirpath, search_parent_directories=True)
    for root, dirnames, filenames in os.walk(repo.working_tree_dir):
        for dirname in dirnames:
            path = os.path.join(root, dirname)
            path = path.replace('\\', '/')
            path = path.replace('"', '')
            path += '/'

            if status_cache.get(path, 'unknown') == 'staged':
                status_cache[path] = 'committed'


def get_git_status(path):
    # repo = git.Repo(path, search_parent_directories=True)
    if not is_git_repository(path):
        return None

    try:
        repo = git.Repo(path, search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        return None

    repo_path = repo.working_tree_dir
    path = path.replace('\\', '/')
    path = path.replace('"', "")
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

        return calculate_status(path)

    return calculate_status(path)


def calculate_status(path):
    # print('starting calculating...')
    repo = git.Repo(path, search_parent_directories=True)
    root_dir = repo.working_tree_dir
    calculated_cache[root_dir] = True
    root_dir = root_dir.replace('\\', '/')
    root_dir = root_dir.replace('"', '')
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
            path = path.replace('"', '')
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
            path = path.replace('"', '')
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
        filepath = filepath.replace('"', '')
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
            path = path.replace('"', '')
            mtime = os.path.getmtime(path)
            path += '/'

            status_cache[path] = status
            mtime_cache[path] = mtime

        for file in files:
            path = os.path.join(root, file)
            path = path.replace('\\', '/')
            path = path.replace('"', '')
            mtime = os.path.getmtime(path)

            status_cache[path] = status
            mtime_cache[path] = mtime