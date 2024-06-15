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


class UploadLake(JSONFileHandler):

    def __init__(self, user_id, timezone='Asia/Seoul'):
        super().__init__(user_id, timezone)
        self.save_directory_id = '1LX3kYUQJJAqR5S_wvud8TNz428sWi5Yh'

    def save_data_and_images(self, extracted_data):
        image_counter = 1
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_folder = os.path.join(self.folder_name, 'temp')
        os.makedirs(temp_folder, exist_ok=True)
        json_path = os.path.join(temp_folder, f'{current_time}.json')

        interactions = []

        for data in extracted_data:
            for interaction in data.interaction:
                # 이미지 파일 이름을 1부터 증가하도록 설정
                img_path = os.path.join(temp_folder, f"{image_counter}.png")
                # 이미지 포인터에서 실제 이미지를 가져와서 저장
                cv2.imwrite(img_path, interaction.image)
                # interaction 객체의 이미지 이름을 업데이트
                interaction.image = f"{image_counter}.png"
                image_counter += 1

            interactions.append(data.to_dict())

        with open(json_path, 'w') as file:
            json.dump(interactions, file, indent=4)

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
            for file in os.listdir(temp_folder):
                zipf.write(os.path.join(temp_folder, file), arcname=file)

        self.upload_to_drive(temp_folder)

    def upload_to_drive(self, temp_folder):
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        SERVICE_ACCOUNT_FILE = '/Users/sukcess/WorkSpace/sink/ai-sink-aa94e4cf6758.json'

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
        shutil.rmtree(temp_folder)
        os.remove(self.zip_path)

        print(f'파일 {os.path.basename(self.zip_path)}가 Google Drive에 업로드되었습니다.')
