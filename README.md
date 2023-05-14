# **Git Scroll - Git 통합 파일 브라우저**

Git Scroll은 Python으로 만들어진 Windows용 GUI 기반 Repository Management Service입니다. File Browsing과 일부 repository 관리 기능을 실행할 수 있으며, 스크롤 및 펼치기/접기를 통해 파일 브라우징 및 repository 관리가 가능하여 Git_Scroll으로 명명되었습니다. 이 특성 덕분에, 여러 git repository를 하나의 창에 표시하고 각각을 따로 관리할 수 있습니다.

PyQt5를 사용하여 GUI를 구현하였으며, GitPython 라이브러리를 통해 Git 저장소와 상호작용합니다.

## **설치 및 환경**

- 환경: 이 프로젝트는 `Windows 11` 환경에서 및 `Python 3.11` 인터프리터를 사용하여 제작 및 실험되었습니다. 일부 다른 버전에서도 정상 작동할 수 있으나 해당 버전의 환경에서 사용하는 것을 추천합니다.

- 설치: 이 프로젝트는 `PyQt5` 및 `GitPython` 라이브러리를 필요로 합니다. 이 라이브러리들은 `requirement.py`를 실행하여 설치할 수 있습니다.

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
- `git_commit`: 선택된 디렉토리가 git repository에 속할 때 실행이 가능합니다. 현재 선택된 디렉토리의 git repository에 대해서 `git commit`을 실행합니다. 현재 staged인 파일의 리스트를 보여주며, 만약 이 파일이 하나도 없거나 commit message가 비어 있다면 실행하지 않습니다.

#### 파일을 선택했을 경우
- `git_add`: `untracked`, `modified` 및 `ignored` 파일에 대해 실행 가능합니다. 해당 파일에 대해 `git add`를 실행합니다. 파일이 `ignored`였다면 `git add -f`를 실행합니다. 해당 파일의 변화 사항을 stage합니다.
- `git_restore`: `modified` 파일에 대해 실행 가능합니다. 해당 파일에 대해 `git restore`를 실행합니다. 파일을 latest commit의 상태로 되돌립니다.
- `git_restore_staged`: `staged` 파일에 대해 실행 가능합니다. 해당 파일에 대해 `git restore --staged`를 실행합니다. 선택된 파일의 staging을 취소합니다.
- `git_rm_cached`: `committed` 파일에 대해 실행 가능합니다. 해당 파일에 대해 `git rm --cached`를 실행합니다. 파일의 추적을 중단하고 변화 사항을 stage합니다.
- `git_rm`: `committed` 파일에 대해 실행 가능합니다. 해당 파일에 대해 `git rm`을 실행합니다. 파일을 삭제하고 변화 사항을 stage합니다.
- `git_mv`: `committed` 파일에 대해 실행 가능합니다. 해당 파일에 대해 `git mv`를 실행합니다. 파일의 이름을 변경하고 변화 사항을 stage합니다.

## **아이콘**
본 프로그램은 프로그램의 상태를 기존의 Untracked/Modified/Staged/Committed의 4가지 상태와 더불어 Ignored라는 상태를 추가로 표현합니다.
- **`Ignored`**: 해당 파일이 `.gitignore`에 의해 무시되고 있는 상태입니다. Untracked와 실행 가능한 명령은 같으며, `Git add`를 사용할 수 있으나 내부적으로는 `git add -f`를 실행합니다. ignored 상태의 파일은 다른 특별한 아이콘으로 표시되지 않고, 해당 파일 본래의 아이콘으로 표시됩니다.

## **사용법**

1. **`python filebrowser.py`**를 실행하여 애플리케이션을 시작합니다.
2. 파일 구조를 탐색하고 Git 상태 아이콘을 확인합니다. Git Repository가 아닌 파일은 Git 상태 아이콘으로 표시되지 않습니다.
3. 파일이나 폴더를 마우스 오른쪽 버튼으로 클릭하여 메뉴를 열고 Git 명령을 실행합니다.

## **라이선스**

이 프로젝트는 GNU GPL-3.0 License에 따라 배포됩니다.
