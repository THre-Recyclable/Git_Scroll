# **Git Scroll - Git 통합 파일 브라우저**

Git Scroll은 Python으로 만들어진 Windows용 GUI 기반 Repository Management Service입니다. File Browsing과 일부 repository 관리 기능을 실행할 수 있으며, 스크롤 및 펼치기/접기를 통해 파일 브라우징 및 repository 관리가 가능하여 Git_Scroll으로 명명되었습니다. 이 특성 덕분에, 여러 git repository를 하나의 창에 표시하고 각각을 따로 관리할 수 있습니다.

PyQt5를 사용하여 GUI를 구현하였으며, GitPython 라이브러리를 통해 Git 저장소와 상호작용합니다.
<img width="393" alt="fileexample" src="https://github.com/THre-Recyclable/Git_Scroll/assets/62564727/4d51dc27-3550-4acd-97b3-1891bcc28404">

이 프로젝트는 다음의 파일 브라우저 시스템을 이용하여 만들어졌습니다.
https://github.com/Hshadow/file-browser-with-python-PyQt5

## **설치 및 환경**

- 환경: 이 프로젝트는 `Windows 11` 환경에서 및 `Python 3.11` 인터프리터를 사용하여 제작 및 실험되었습니다. 일부 다른 버전에서도 정상 작동할 수 있으나 해당 버전의 환경에서 사용하는 것을 추천합니다.

- 설치: python 인터프리터가 필요하며, 추가로 이 프로젝트는 `PyQt5` 및 `GitPython` 라이브러리를 필요로 합니다. 이 라이브러리들은 `requirement.py`를 실행하거나, `pip install pyqt5` 및 `pip install gitpython`을 실행하여 설치할 수 있습니다. 또한 git이 설치되어 있어야 합니다.

- **주의** : python이 설치된 경로에 한글이 있거나, Git Scroll이 존재하는 경로에 한글이 있으면 정상 동작하지 않을 수 있습니다.




## **파일 구조**

- **`filebrowser.py`**: Main script입니다. GUI를 설정하고, Model-View architecture를 설정하며, 여러 이벤트에 대한 신호를 슬롯에 연결합니다.

- **`gitfilestate.py`**: `QFileSystemModel`의 서브 클래스인 `GitFileState` 클래스를 정의합니다. 이 클래스는 파일의 Git 상태에 따른 사용자 정의 아이콘을 반환합니다.

- **`status.py`**: `GitPython` 라이브러리로 Git 저장소와 상호작용하여 화면에 표시되는 각 파일의 상태(Untracked, Modified, Staged, Committed, Ignored)를 계산하는 함수를 포함하고 있습니다.

- **`requirements.py`**: 필요한 라이브러리를 설치하는 script입니다.




## **기능**

- 파일 브라우징: 파일 구조를 보여주고 디렉토리를 탐색할 수 있습니다.

- Git 상태 아이콘: 각 파일 옆에 Git 상태를 나타내는 아이콘을 표시합니다.

- 컨텍스트 메뉴: 파일이나 폴더를 마우스 오른쪽 버튼으로 클릭하면 직접 실행할 수 있는 다양한 Git 명령을 제공하는 메뉴가 열립니다.

- Git 명령: 메뉴는 선택된 파일의 Git 상태에 따라 다른 Git 명령을 제공합니다. 예를 들어, **`git add`**, **`git restore`**, **`git rm`**, **`git mv`** 등의 명령을 실행할 수 있습니다.

Git_Scroll은 선택된 것이 파일인지 디렉토리인지에 따라, 만약 파일이라면 파일의 상태에 따라 실행 가능한 메뉴가 다릅니다.
모든 파일은 기본적으로 Open이 가능합니다(Git repository가 아니더라도).

#### 디렉토리를 선택했을 경우
- `git_init`: 선택된 디렉토리에 대해 `git init`을 실행하여 git repository를 초기화합니다.

- `git_commit`: 선택된 디렉토리가 git repository에 속할 때 실행이 가능합니다. 현재 선택된 디렉토리의 git repository에 대해서 `git commit`을 실행합니다. 현재 staged인 파일의 리스트를 보여주며, 만약 이 파일이 하나도 없거나 commit message가 비어 있다면 실행을 취소합니다.

#### 파일을 선택했을 경우

- `git_add`: `untracked`, `modified` 및 `ignored` 파일에 대해 실행 가능합니다. 해당 파일에 대해 `git add`를 실행합니다. 파일이 `ignored`였다면 `git add -f`를 실행합니다. 해당 파일의 변화 사항을 stage합니다.

- `git_restore`: `modified` 파일에 대해 실행 가능합니다. 해당 파일에 대해 `git restore`를 실행합니다. 파일을 latest commit의 상태로 되돌립니다.

- `git_restore_staged`: `staged` 파일에 대해 실행 가능합니다. 해당 파일에 대해 `git restore --staged`를 실행합니다. 선택된 파일의 staging을 취소합니다.

- `git_rm_cached`: `committed` 파일에 대해 실행 가능합니다. 해당 파일에 대해 `git rm --cached`를 실행합니다. 파일의 추적을 중단하고 변화 사항을 stage합니다.

- `git_rm`: `committed` 파일에 대해 실행 가능합니다. 해당 파일에 대해 `git rm`을 실행합니다. 파일을 삭제하고 변화 사항을 stage합니다.

- `git_mv`: `committed` 파일에 대해 실행 가능합니다. 해당 파일에 대해 `git mv`를 실행합니다. 파일의 이름을 변경하고 변화 사항을 stage합니다. 바꾸고자 하는 이름이 이미 같은 디렉토리 내에 존재한다면 실행을 취소합니다.




## **아이콘**

본 프로그램은 프로그램의 상태를 기존의 Untracked/Modified/Staged/Committed의 4가지 상태와 더불어 Ignored라는 상태를 추가로 표현합니다.
- **`Ignored`**: 해당 파일이 `.gitignore`에 의해 무시되고 있는 상태입니다. Untracked와 실행 가능한 명령은 같으며, `Git add`를 사용할 수 있으나 내부적으로는 `git add -f`를 실행합니다. ignored 상태의 파일은 다른 특별한 아이콘으로 표시되지 않고, 해당 파일 본래의 아이콘으로 표시됩니다.
<img width="254" alt="iconex" src="https://github.com/THre-Recyclable/Git_Scroll/assets/62564727/db16475c-8b6b-41f3-b77a-f7365457fc31">




## 디렉토리 상태

본 프로그램은 개별 파일의 상태 뿐만 아니라 repository 내의 디렉토리에 대해서도 상태 변화를 추적하며, 다음과 같은 규칙을 따릅니다.

#### 단, git repository의 root 디렉토리는 상태 변화를 표시하지 않습니다.

- 우선순위는 Untracked > Modified > Staged > Committed > Ignored 입니다.

- 디렉토리 내의 우선순위가 가장 높은 파일의 상태가 해당 파일을 포함하고 있는 디렉토리에도 적용됩니다. (예시: 만약 디렉토리 내에 Modified 파일 2개와 Staged 파일 10개, Committed 파일 100개가 존재할 경우, 디렉토리의 상태는 Modified가 됩니다)

- 예외적으로, 새로 생성된, 아무 파일도 포함하지 않는 디렉토리는 Committed로 표시됩니다.

  - Git_Scroll은 내부적으로 `git status --porcelain --ignored`의 결과를 parsing하여 파일의 상태 변화를 감지합니다. 그러나 새로 생성된 아무 파일도 포함하지 않는 디렉토리는 이러한 명령어를 수행했을 때 표시되지 않으므로, 기본 상태인 Committed로 표현됩니다.
  
  - 단, 아무 파일도 존재하지 않는 디렉토리라고 하더라도, 자신의 상위 디렉토리가 untracked이거나 ignored 상태라면, 해당 디렉토리는 상위 디렉토리의 상태를 따라 가게 됩니다.




## **사용법**

1. **`python filebrowser.py`**를 실행하여 애플리케이션을 시작합니다.
2. 파일 구조를 탐색하고 Git 상태 아이콘을 확인합니다. Git Repository가 아닌 파일은 Git 상태 아이콘으로 표시되지 않습니다.
3. 파일이나 폴더를 마우스 오른쪽 버튼으로 클릭하여 메뉴를 열고 Git 명령을 실행합니다.




## **(중요) 사용 시 주의사항**

- Git Scroll은 repository 내의 상태 변화를 대부분 추적하지만, 본 프로그램 외에 다른 프로그램을 통해 git을 관리할 경우 그 변화 사항이 즉시 반영됨을 보장하지 않습니다. 특히, Git Scroll이 실행된 상태에서 명령 프롬프트 혹은 다른 git 관리 프로그램을 통해 `git commit`을 실행할 경우, `staged` 파일이 `committed`로 바뀌지 않고 계속해서 `staged`로 남게 됩니다. 이 때에는 Git Scroll을 재실행하거나, 해당 repository 내의 다른 파일에 대한 git function을 수행해서 repository가 상태 변화를 다시 계산하도록 하면 변화 사항이 정상적으로 반영됩니다.

- 디렉토리는 상태 변화의 추적 및 `git init`, `git commit`만을 제공하고, 이 외에 디렉토리 단위의 git function은 지원하지 않습니다.

- **(중요)** 경로 내에 한글이 존재할 경우 정상 작동하지 않을 수 있습니다. Git Scroll은 `git status`의 실행 결과를 parsing하여 파일의 상태 변화를 계산합니다. 따라서 `git status`에서 부적절한 결과가 나온다면(한글 경로를 제대로 표현하지 못한다면) Git Scroll이 제대로 작동하지 못합니다. 특히 새로 생성된 파일의 이름이 자동으로 한글로 설정될 경우에 주의해야 합니다(예시: `새 텍스트 파일.txt`, `새 폴더`). 이  때에는 다음과 같은 방법을 추천합니다:

  - git repository의 밖에서 파일을 생성하고 이름을 영문으로 바꾼 뒤, git repository로 이동시킵니다.

  - 또는, git repository 디렉토리를 접어서 내부 파일을 보여주지 않는 상태로 만든 다음, 해당 디렉토리 내에 파일을 만들고 영문으로 이름을 변경합니다.

- Git Scroll을 화면의 일부분에 띄워둔 상태에서 파일을 수정할 경우, modified 상태가 GUI에 반영되지 않는 것처럼 보일 수 있습니다. 이 때에는 Git Scroll을 클릭해서 프로그램을 다시 활성 상태로 만들어주면 상태 변화가 반영됩니다.

- Git Scroll은 git에서 실행이 불가능한 명령을 수행하지 못합니다(예시: commit object가 없는 상태에서 파일을 stage한 뒤 `git restore --staged`를 하는 경우).

- 우클릭으로 메뉴를 불러올 때, 파일의 이름이 존재하는 부분이 아니라 다른 부분을 클릭하여 메뉴를 불러오면 git function이 정상 동작하지 않습니다. (예시: 파일의 용량, 수정 날짜 등을 우클릭하는 경우)


## **라이선스**

이 프로젝트는 GNU GPL-3.0 License에 따라 배포됩니다.
