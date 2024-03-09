# 내장
import os
import time

# 서드파티
import requests
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수 설정
CD_GITHUB_TOKEN = os.getenv('CD_GITHUB_TOKEN')
CD_GITHUB_BRANCH = os.getenv('CD_GITHUB_BRANCH')
CD_GITHUB_REPO_NAME = os.getenv('CD_GITHUB_REPO_NAME')
CD_POLLING_INTERVAL_SECONDS = int(os.getenv('CD_POLLING_INTERVAL_SECONDS'))

# 마지막으로 확인한 커밋 SHA 저장
last_seen_commit_sha = None


def fetch_latest_commit_sha():
    url = f'https://api.github.com/repos/{CD_GITHUB_REPO_NAME}/commits/{CD_GITHUB_BRANCH}'
    headers = {'Authorization': f'token {CD_GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 요청 실패 시 예외 발생
    data = response.json()
    return data['sha']


def update_and_deploy():
    # 여기에 프로젝트 루트 디렉토리에서 코드를 업데이트하고 재배포하는 로직을 구현합니다.
    # 예: Git pull을 사용하여 최신 코드를 가져오고 필요한 배포 스크립트를 실행합니다.
    print('Detected new commit. Updating and deploying...')
    os.system('git pull')
    # 필요한 경우 여기에 추가 배포 명령을 실행할 수 있습니다.


while True:
    try:
        print('Checking for updates...')
        latest_commit_sha = fetch_latest_commit_sha()
        if last_seen_commit_sha is None:
            last_seen_commit_sha = latest_commit_sha

        if latest_commit_sha != last_seen_commit_sha:
            update_and_deploy()
            last_seen_commit_sha = latest_commit_sha
        else:
            print('No updates found.')

        time.sleep(CD_POLLING_INTERVAL_SECONDS)

    except Exception as e:
        print(f'Error checking for updates: {e}')
        # 에러 발생 시 다음 폴링 시간까지 대기
        time.sleep(CD_POLLING_INTERVAL_SECONDS)
