# **Git Scroll - Git 통합 파일 브라우저**

Git Scroll은 File Browsing과 Git 작업을 결합한 프로그램입니다. PyQt5를 사용하여 GUI를 구현하였으며, GitPython 라이브러리를 통해 Git 저장소와 상호작용합니다.

## **설치**

이 프로젝트는 PyQt5 및 GitPython을 필요로 합니다. 이 라이브러리들은 **`requirement.py`**를 실행하여 설치할 수 있습니다.

## **파일 구조**

- **`filebrowser.py`**: Main script입니다. GUI를 설정하고, Model-View architecture를 설정하며, 여러 이벤트에 대한 신호를 슬롯에 연결합니다.
- **`gitfilestate.py`**: **`QFileSystemModel`**의 서브 클래스인 **`GitFileState`** 클래스를 정의합니다. 이 클래스는 파일의 Git 상태에 따른 사용자 정의 아이콘을 반환합니다.
- **`status.py`**: GitPython 라이브러리를 사용하여 Git 저장소와 상호작용하는 is_git_repository, get_status를 포함하고 있습니다.
- **`requirements.py`**: 필요한 라이브러리를 설치하는 script입니다.

## **기능**

- 파일 브라우징: 파일 구조를 보여주고 디렉토리를 탐색할 수 있습니다.
- Git 상태 아이콘: 각 파일 옆에 Git 상태를 나타내는 아이콘을 표시합니다.
- 컨텍스트 메뉴: 파일이나 폴더를 마우스 오른쪽 버튼으로 클릭하면 직접 실행할 수 있는 다양한 Git 명령을 제공하는 메뉴가 열립니다.
- Git 명령: 메뉴는 선택된 파일의 Git 상태에 따라 다른 Git 명령을 제공합니다. 예를 들어, **`git add`**, **`git restore`**, **`git rm`**, **`git mv`** 등의 명령을 실행할 수 있습니다.

## **사용법**

1. **`python filebrowser.py`**를 실행하여 애플리케이션을 시작합니다.
2. 파일 구조를 탐색하고 Git 상태 아이콘을 확인합니다.
3. 파일이나 폴더를 마우스 오른쪽 버튼으로 클릭하여 메뉴를 열고 Git 명령을 실행합니다.

## **라이선스**

이 프로젝트는 MIT 라이선스에 따라 배포됩니다.