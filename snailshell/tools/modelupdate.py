import os
import wandb
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ModelUpdater:

    def __init__(self, project_name, artifact_name, aliases, base_model_path,
                 api_key):
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
            artifact = api.artifact(
                f'{self.project_name}/{self.artifact_name}:latest')
            artifact_aliases = artifact.aliases
            if all(alias in artifact_aliases for alias in self.aliases):
                logging.info(
                    f"Found model artifact: {artifact.name} with aliases {artifact_aliases}"
                )
                return artifact
            logging.warning(
                "No model artifact with the specified aliases found.")
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
                logging.info(
                    f"Deleted local model folder: {self.base_model_path}")
            else:
                logging.warning(
                    f"Local model folder {self.base_model_path} does not exist."
                )
        except Exception as e:
            logging.error(f"Failed to delete local model folder: {e}")
            raise

    def update_model(self):
        self.authenticate_wandb()
        model_artifact = self.get_model_artifact()
        if model_artifact:
            self.delete_local_model_folder()
            self.download_artifact_folder(model_artifact)
            logging.info(
                f"Downloaded and updated the model folder to {self.base_model_path}."
            )
        else:
            logging.info(
                "No matching model found in Wandb. Keeping the local model folder."
            )
