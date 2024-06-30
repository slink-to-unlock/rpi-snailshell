import os
import json
import zipfile
import cv2
import shutil
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from autosink_data_elt.log.filehandler import JSONFileHandler


class DatalakeUploader(JSONFileHandler):

    def __init__(self, user_id, timezone='Asia/Seoul'):
        super().__init__(user_id, timezone)
        self.save_directory_id = os.getenv('DRIVE_FOLDER_ID')

    def save_data_and_images(self, extracted_data):
        for index, data in enumerate(extracted_data, start=1):
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{self.dishwashing_id}_{index}"
            temp_folder = os.path.join(self.folder_name, folder_name)
            os.makedirs(temp_folder, exist_ok=True)
            json_path = os.path.join(temp_folder, f'{current_time}.json')

            image_counter = 1
            for interaction in data.interactions:
                # 이미지 파일 이름을 1부터 증가하도록 설정
                img_path = os.path.join(temp_folder, f"{image_counter}.png")
                # 이미지 포인터에서 실제 이미지를 가져와서 저장
                cv2.imwrite(img_path, interaction.image)
                # interaction 객체의 이미지 이름을 업데이트
                interaction.image = f"{image_counter}.png"
                image_counter += 1

            with open(json_path, 'w') as file:
                json.dump(data.to_dict(), file, indent=4)

            # ZIP 파일 생성 및 업로드
            self.zip_and_upload(temp_folder, current_time)

    def write_file(self, data, path):
        with open(path, 'w') as file:
            json.dump(data.to_dict(), file, indent=4)
        self.image_counter = 0  # Reset the image counter after writing to file
        logger.info(f'Wrote data to {path} and reset image counter')

    def zip_and_upload(self, temp_folder, current_time):
        self.zip_path = f"{current_time}.zip"

        with zipfile.ZipFile(self.zip_path, 'w') as zipf:
            for root, _, files in os.walk(temp_folder):
                for file in files:
                    zipf.write(
                        os.path.join(root, file),
                        arcname=os.path.relpath(os.path.join(root, file), temp_folder)
                    )

        self.upload_to_drive()

    def upload_to_drive(self):
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        SERVICE_ACCOUNT_FILE = os.getenv('DRIVE_API_KEY_PATH')

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)

        file_metadata = {
            'name': os.path.basename(self.zip_path),
            'parents': [self.save_directory_id]
        }
        media = MediaFileUpload(self.zip_path, mimetype='application/zip')
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        # 임시 파일 및 디렉토리 정리
        shutil.rmtree(self.folder_name)
        os.remove(self.zip_path)

        print(f'파일 {os.path.basename(self.zip_path)}가 Google Drive에 업로드되었습니다.')
