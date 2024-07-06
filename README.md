# Snailshell for RPi

![red-snail](docs/red-snail.png)

## 필요 준비물

- 릴레이
- 아두이노 우노보드
- 솔레노이드 밸브
- 라즈베리파이 카메라
- 라즈베리파이 > 4B+
- 라즈비안 OS **64 Bit**

## 구성도

`TODO`

## 사용 방법

`TODO`

## 라즈베리파이 세팅

### 한글 설정

```bash
sudo apt-get install -y fonts-unfonts-core ibus ibus-hangul
sudo reboot
```

### 환경 변수 설정

모델 업데이트에 사용될 wandb와 datalake로 사용될 google drive folder의 고유 ID, google drive의 api키를 환경 변수로 설정하세요.

```bash
export WANDB_API_KEY='your_wandb_api_key'
export DRIVE_API_KEY_PATH='your_google_drive_api_key'
export DRIVE_FOLDER_ID='your_google_drive_folder_id'
export DISCORD_WEBHOOK_URL='your_discord_webhook_url'
```

## 개발 문서

[Github repository](https://github.com/slink-to-unlock/rpi-snailshell)의 [docs/README-dev](docs/README-dev.md) 참고
