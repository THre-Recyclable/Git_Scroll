# **Git Scroll - An Integrated Git File Browser**

Git Scroll is a GUI-based Repository Management Service for Windows, developed in Python. It provides file browsing and some repository management functionalities, allowing file browsing and repository management through scrolling and expanding/collapsing features. That's why it is named Git_Scroll. Thanks to these features, multiple git repositories can be displayed in one window and each can be managed separately.

It utilizes PyQt5 to construct the GUI, and the GitPython library for interaction with Git repositories.
<img width="760" alt="fileexample" src="https://github.com/THre-Recyclable/Git_Scroll/assets/62564727/d4595416-0e41-43c1-adad-df13e525edb4">

This project was created using the following file browser system:
https://github.com/Hshadow/file-browser-with-python-PyQt5

## **Installation & Environment**

- Environment: This project was developed and tested in a Windows 11 environment using the Python 3.11 interpreter. Although it may work fine with other versions, it is recommended to use it in this specific environment.

- Installation: A Python interpreter is necessary. Also, this project requires the PyQt5 and GitPython libraries. These libraries can be installed either by running requirement.py or by executing `pip install pyqt5` and `pip install gitpython`. Moreover, git needs to be installed.

- **Note** : If there are Korean characters in the path where Python is installed or in the path where Git Scroll exists, it may not function properly.




## **File Structure**

- **`filebrowser.py`**: This is the main script. It sets up the GUI, establishes the Model-View architecture, and connects signals to slots for various events.

- **`gitfilestate.py`**: Defines the `GitFileState` class, a subclass of QFileSystemModel. This class returns custom icons according to the Git status of the file.

- **`status.py`**: Contains functions that interact with Git repositories via the `GitPython` library to calculate the status (Untracked, Modified, Staged, Committed, Ignored) of each file displayed on the screen.

- **`requirements.py`**: This script installs the necessary libraries.

- **`commitHistory.py`**: Defines functions and classes needed for displaying commit history.

- **`credentials.txt`**: The ID and personal access token used to clone private repositories are stored here. It is recommended not to modify the contents arbitrarily.




## **Features**

- File Browsing: Displays file structure and allows navigating through directories.

- Git Status Icons: Displays an icon indicating the Git status next to each file.

- Context Menu: Provides a menu offering various Git commands that can be executed directly by right-clicking a file or folder.

- Git Commands: The menu offers different Git commands depending on the Git status of the selected file. For instance, it allows running commands like `git add`, `git restore`, `git rm`, `git mv`, and some branch-related commands.

- Current Branch: If the selected directory is a git repository, the current branch is displayed in the lower right corner.
<img width="377" alt="current branch" src="https://github.com/THre-Recyclable/Git_Scroll/assets/62564727/27ed1b4f-01fe-49d3-a3c6-c2004b807355">

The Git_Scroll displays different executable menus depending on whether the selected item is a file or a directory, and if it's a file, depending on the file's status. All files can be opened by default (even if they are not in a Git repository).

#### When a Directory is Selected
- `git_init`: Executes `git init` on the selected directory, initializing it as a git repository. Can only be executed on directories that are not part of a git repository.

- `git_commit`: Can be executed when the selected directory is part of a git repository. Executes `git commit` on the git repository of the currently selected directory. Displays a list of currently staged files. If there are no such files or the commit message is empty, the execution is canceled.

- `branch_create`: (for git repository) Creates a new branch. Does not work if the name already exists or is blank.

- `branch_delete`: (for git repository) Deletes the selected branch. The current branch cannot be deleted.

- `branch_rename`: (for git repository) Renames a branch. The name of the current branch cannot be changed.

- `branch_merge`: (for git repository) Merges the selected branch into the current branch. If there are no other branches than the current one, it does not run. If the merge fails due to conflict, it displays the unmerged path.

- `commit history`: (for git repository) Outputs the commit history of the selected git repository's current branch in table form. Clicking each row displays detailed information about the corresponding commit object.

- `git_clone`: Clones a GitHub repository. It only works with HTTPS links. For cloning a private repository, an ID and a personal access token are required in addition to the URL. If the clone is successful, it saves the used ID and personal access token, allowing you to skip entering them the next time you run `git_clone` using the `Try with saved credentials` option.



#### When a File is Selected

- `git_add`: Available for `untracked`, `modified`, and `ignored` files. Executes `git add` on the file. If the file is `ignored`, it runs `git add -f`. This stages changes in the file.

- `git_restore`: Available for `modified` files. Executes `git restore` on the file, reverting the file to the state of the latest commit.

- `git_restore_staged`: Available for `staged` files. Executes `git restore --staged` on the file. This cancels staging of the selected file.

- `git_rm_cached`: Available for `committed` files. Executes `git rm --cached` on the file. This stops tracking the file and stages the changes.

- `git_rm`: Available for `committed` files. Executes `git rm` on the file. This deletes the file and stages the changes.

- `git_mv`: Available for `committed` files. Executes `git mv` on the file. This changes the name of the file and stages the changes. If the new name already exists in the same directory, the execution is canceled.




## **Icons**

This program expresses not only the original states of Untracked/Modified/Staged/Committed, but also an additional state called Ignored.
- **`Ignored`**: This means the file is being ignored by `.gitignore`. The executable commands are the same as Untracked, and `git add` can be used, but internally it executes `git add -f`. Files in the ignored state are not marked with any special icon and are displayed with the original icon of the file.
<img width="508" alt="iconex" src="https://github.com/THre-Recyclable/Git_Scroll/assets/62564727/db16475c-8b6b-41f3-b77a-f7365457fc31">


## File State

If a file exists in multiple states, it is displayed in the priority order of Untracked > Modified > Staged > Committed > Ignored.


## Directory State

This program also tracks the status changes of directories within the repository, following these rules:

#### Note that the root directory of the git repository does not show status changes.

- The priority is Untracked > Modified > Staged > Committed > Ignored.

- The status of the file with the highest priority in the directory applies to the directory containing that file. (Example: If a directory contains 2 Modified files, 10 Staged files, and 100 Committed files, the status of the directory will be Modified)

- Exceptionally, a newly created directory that contains no files is marked as Committed.

  - Git_Scroll internally parses the result of `git status --porcelain --ignored` to detect file state changes. However, a newly created directory that contains no files does not appear when executing this command, so it is expressed as the default state, Committed.
  
  - However, even if a directory does not contain any files, if the parent directory is in the untracked or ignored state, the directory will follow the state of the parent directory.




## **How to Use**

1. Start the application by running `python filebrowser.py`.
2. Browse the file structure and check the Git status icons. Files that are not Git Repositories are not displayed with Git status icons.
3. Open the menu by right-clicking a file or folder and execute Git commands.




## **(Important) Precautions When Using**

- While Git Scroll tracks most state changes in the repository, it does not guarantee that changes made through other programs managing git will be immediately reflected. Especially when `git commit` is executed via the command prompt or another git management program while Git Scroll is running, `staged` files do not change to `committed` and remain as `staged`. In this case, rerun Git Scroll or perform a git function on another file in the repository to recalculate the repository's state changes, and the changes will be properly reflected.

- Directories only provide status tracking and `git init`, `git commit`, `git clone` and some branch commands. Git_Scroll does not support directory-level git functions.

- **(Important)** It may not work properly if there is Korean in the path. Git Scroll parses the execution result of `git status` to calculate the state change of the file. Therefore, if `git status` gives an inappropriate result (if it does not properly represent the Korean path), Git Scroll will not work properly. This is particularly important when the name of a newly created file is automatically set to Korean (example: `새 텍스트 파일.txt`, `새 폴더`). In this case, the following methods are recommended:

  - Create a file outside of the git repository, change the name to English, and then move it to the git repository.

  - Or, fold the git repository directory so that it does not show internal files, create a file in that directory, and change the name to English.

- If you modify files while displaying Git Scroll in part of the screen, the modified state may not appear to be reflected in the GUI. In this case, click Git Scroll to reactivate the program and the state change will be reflected.

- Git Scroll cannot perform commands that are unexecutable in git (example: after staging a file when there is no commit object, running `git restore --staged`).


## **License**

This project is distributed under the GNU GPL-3.0 License.
