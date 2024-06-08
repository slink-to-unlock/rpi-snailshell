import os
import json
import zipfile
import cv2
import shutil
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from autosink_data_elt.log import filehandler


class UploadLake(filehandler.JSONFileHandler):

    def __init__(self, user_id, timezone='Asia/Seoul'):
        super().__init__(user_id, timezone)
        self.save_directory_id = '1LX3kYUQJJAqR5S_wvud8TNz428sWi5Yh'
        self.zip_path = f"{self.folder_name}.zip"

    def save_data_and_images(self, extracted_data, run_images):
        # 데이터 초기화 및 저장
        data = self.create_default_data(version=2)

        # 이미지 및 상호작용 데이터 처리
        for interaction_key, interactions in extracted_data.items():
            for interaction_data in interactions:
                timestamp = interaction_data["timestamp"]
                model_output = interaction_data["model_output"]
                magnetic = interaction_data["magnetic"]
                image = cv2.imread(interaction_data["image"])
                img_path = os.path.join(self.folder_name,
                                        f"{self.image_counter}.png")
                cv2.imwrite(img_path, image)
                interaction_data["image"] = img_path
                # 상호작용 추가
                data = self.add_interaction(data,
                                            timestamp=timestamp,
                                            model_output=model_output,
                                            magnetic=magnetic)

        self.write_file(data)

        # ZIP 파일 생성 및 업로드
        self.zip_and_upload()

    def zip_and_upload(self):
        with zipfile.ZipFile(self.zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(self.folder_name):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=file)
            json_file_path = os.path.join(self.folder_name,
                                          'interactions.json')
            zipf.write(json_file_path)

        self.upload_to_drive()

    def upload_to_drive(self):
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        SERVICE_ACCOUNT_FILE = '/path/to/your/service-account.json'

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=credentials)

        file_metadata = {
            'name': os.path.basename(self.zip_path),
            'parents': [self.save_directory_id]
        }
        media = MediaFileUpload(self.zip_path, mimetype='application/zip')
        service.files().create(body=file_metadata,
                               media_body=media,
                               fields='id').execute()

        # 임시 파일 및 디렉토리 정리
        shutil.rmtree(self.folder_name)
        os.remove(self.zip_path)

        print(f'파일 {os.path.basename(self.zip_path)}가 Google Drive에 업로드되었습니다.')
