# 내장
import time

# 서드파티
import torch
import numpy as np
from transformers import ResNetForImageClassification, AutoImageProcessor

# 프로젝트
from snailshell.adapters.base import ModelAdapter


class ResNetAdapter(ModelAdapter):

    def __init__(
        self,
        weight_path,
        pretrained_model_name="microsoft/resnet-50",
    ):
        super().__init__(weight_path)
        self.model = ResNetForImageClassification.from_pretrained(weight_path)
        #resnet는 model.eval()을 하지 않아도 되는것인지?
        self.processor = AutoImageProcessor.from_pretrained(pretrained_model_name)

    def preprocess(
        self,
        image: np.array,
    ):
        return self.processor(images=image, return_tensors="pt")

    def predict(
        self,
        image: np.array,
    ) -> int:
        inputs = self.preprocess(image)
        start_predict = time.time()
        outputs = self.model(**inputs)
        print('image predice time:', time.time() - start_predict)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()
        return predicted_class
