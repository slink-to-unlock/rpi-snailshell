import os
import json
import zipfile
import datetime
import cv2
import shutil
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account


class DataExtraction:

    @staticmethod
    def Upload(extracted_images, extracted_labels):
        # 날짜를 기준으로 파일 이름 생성
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        json_filename = f"{date_str}.json"
        zip_filename = f"{date_str}.zip"
        save_path = date_str
        zip_path = zip_filename
        save_directory_id = '1LX3kYUQJJAqR5S_wvud8TNz428sWi5Yh'

        # 이미지 및 라벨을 저장할 디렉토리 생성
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # JSON 데이터 준비
        json_data = []

        # 이미지 파일 저장
        image_filenames = []
        for idx, images in enumerate(extracted_images):
            for img_idx, img in enumerate(images):
                img_filename = f"{date_str}_{idx * len(images) + img_idx + 1}.jpg"
                full_img_path = os.path.join(save_path, img_filename)
                cv2.imwrite(full_img_path, img)
                image_filenames.append(full_img_path)
                # JSON 데이터 추가
                json_data.append({"image": img_filename, "label": extracted_labels[idx][img_idx]})

        # JSON 파일 생성
        json_file_path = os.path.join(save_path, json_filename)
        with open(json_file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

        # ZIP 파일 생성
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in image_filenames:
                zipf.write(file)
            zipf.write(json_file_path)

        # Google Drive에 파일 업로드
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        SERVICE_ACCOUNT_FILE = '/Users/sukcess/Downloads/ai-sink-aa94e4cf6758.json'

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)

        file_metadata = {
            'name': zip_filename,
            'parents': [save_directory_id]  # 파일을 업로드할 폴더 ID
        }
        media = MediaFileUpload(zip_path, mimetype='application/zip')
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        # 임시 파일 및 디렉토리 정리
        for file in image_filenames:
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists(json_file_path):
            os.remove(json_file_path)
        if os.path.exists(save_path):
            shutil.rmtree(save_path)
        if os.path.exists(zip_path):
            os.remove(zip_path)

        print(f'파일 {zip_filename} 이(가) Google Drive에 업로드되었습니다.')
