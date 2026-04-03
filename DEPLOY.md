# 🚀 Render 배포 가이드 (GitHub 연동)

이 문서는 로컬의 워드클라우드 프로젝트를 깃허브에 올리고 Render.com에 배포하는 방법을 설명합니다.

## 1단계: 깃허브(GitHub) 저장소에 코드 올리기

1.  [GitHub](https://github.com/)에 로그인하고 **New Repository**를 생성합니다.
    - Repository name: `word-cloud-app` (원하는 이름)
    - Public/Private 중 선택
2.  로컬 프로젝트 폴더(`c:\Users\agrow\OneDrive\Desktop\wordcloud`)에서 터미널(CMD 또는 PowerShell)을 엽니다.
3.  다음 명령어를 순서대로 입력합니다:
    ```bash
    git init
    git add .
    git commit -m "Initial commit for Render deployment"
    git branch -M main
    git remote add origin https://github.com/사용자이름/word-cloud-app.git
    git push -u origin main
    ```
    *(GitHub Desktop 프로그램을 사용하시면 더 편리하게 올리실 수 있습니다.)*

## 2단계: Render.com에서 앱 배포하기

1.  [Render](https://dashboard.render.com/)에 접속하여 GitHub 계정으로 로그인합니다.
2.  **+ New** 버튼을 누르고 **Web Service**를 선택합니다.
3.  방금 생성한 `word-cloud-app` 저장소를 검색하여 연결(**Connect**)합니다.
4.  설정 화면에서 다음 항목을 확인/수정합니다:
    - **Name**: `word-cloud-app`
    - **Runtime**: `Python 3`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `gunicorn app:app` (또는 `python app.py`)
5.  **Create Web Service** 버튼을 클릭합니다.

## 3단계: 확인

- Render 대시보드에서 빌드 로그가 완료될 때까지 기다립니다.
- 상단에 표시되는 `https://word-cloud-app.onrender.com` 주소로 접속하여 테스트합니다.

---

### 💡 팁
- **폰트**: `NanumGothic.ttf` 파일이 프로젝트 루트에 있어 리눅스 환경에서도 한글이 잘 보입니다.
- **포트**: `app.py`에 `os.environ.get('PORT', 5000)` 설정이 되어 있어 Render가 자동으로 포트를 할당합니다.
