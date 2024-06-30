import os
import wandb
import logging
import shutil


class ModelDownloader:
    """
    Weights and Biases (Wandb)를 사용하여 모델 업데이트를 처리하는 클래스.

    이 클래스는 Wandb와의 인증, 모델 아티팩트 검색, 아티팩트 다운로드 및 
    로컬 모델 폴더 업데이트를 위한 메서드를 제공합니다.

    Args:
        project_name (str): Wandb 프로젝트 이름.
        artifact_name (str): 모델 아티팩트 이름.
        aliases (list): 모델 아티팩트를 식별하기 위한 별칭 목록.
        base_model_path (str): 모델 파일이 저장되는 로컬 경로.
        api_key (str): 인증을 위한 Wandb API 키.

    Method:
        authenticate_wandb(): 제공된 API 키를 사용하여 Wandb와 인증합니다.
        get_model_artifact(): Wandb에서 모델 아티팩트를 검색합니다.
        download_artifact_folder(artifact): 아티팩트를 다운로드합니다.
        delete_local_model_folder(): 로컬 모델 폴더를 삭제합니다.
        update_model(): 모델 업데이트를 수행합니다.
    """

    def __init__(
        self,
        project_name,
        artifact_name,
        aliases,
        base_model_path,
        api_key,
    ):
        self.project_name = project_name
        self.artifact_name = artifact_name
        self.aliases = aliases
        self.base_model_path = base_model_path
        self.api_key = api_key

    def authenticate_wandb(self):
        try:
            os.environ["WANDB_API_KEY"] = self.api_key
            wandb.login(key=self.api_key)
            logging.info("Successfully authenticated with Wandb.")
        except Exception as e:
            logging.error(f"Failed to authenticate with Wandb: {e}")
            raise

    def get_model_artifact(self):
        try:
            api = wandb.Api()
            artifact = api.artifact(f'{self.project_name}/{self.artifact_name}:latest')
            artifact_aliases = artifact.aliases
            if all(alias in artifact_aliases for alias in self.aliases):
                logging.info(
                    f"Found model artifact: {artifact.name} with aliases {artifact_aliases}"
                )
                return artifact
            logging.warning("No model artifact with the specified aliases found.")
            return None
        except Exception as e:
            logging.error(f"Failed to get model from Wandb: {e}")
            raise

    def download_artifact_folder(self, artifact):
        try:
            model_dir = artifact.download(root=self.base_model_path)
            logging.info(f"Artifact downloaded to directory: {model_dir}")
            return model_dir
        except Exception as e:
            logging.error(f"Failed to download artifact folder: {e}")
            raise

    def delete_local_model_folder(self):
        try:
            if os.path.exists(self.base_model_path):
                shutil.rmtree(self.base_model_path)
                logging.info(f"Deleted local model folder: {self.base_model_path}")
            else:
                logging.warning(f"Local model folder {self.base_model_path} does not exist.")
        except Exception as e:
            logging.error(f"Failed to delete local model folder: {e}")
            raise

    def update_model(self):
        self.authenticate_wandb()
        model_artifact = self.get_model_artifact()
        if model_artifact:
            self.delete_local_model_folder()
            self.download_artifact_folder(model_artifact)
            logging.info(f"Downloaded and updated the model folder to {self.base_model_path}.")
        else:
            logging.info("No matching model found in Wandb. Keeping the local model folder.")
