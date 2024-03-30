import torch
import numpy as np
from torchvision import transforms
import torchvision.transforms as transforms
from transformers import ResNetForImageClassification, AutoImageProcessor
from snailshell.model_class import CustomMobileNetV2
from abc import ABC, abstractmethod

import time


# 부모 ABC
class ModelAdapter(ABC):

    def __init__(self, weight_path):
        self.weight_path = weight_path

    @abstractmethod
    def preprocess(self, image: np.array):
        pass

    @abstractmethod
    def predict(self, image: np.array) -> int:
        pass


# mobilenet class
class MobileNetAdapter(ModelAdapter):
    # class를 선언할 때 weight_path를 입력받아 모델과 전처리기 한번만 선언 후 함수를 통해 예측.
    def __init__(self, weight_path):
        super().__init__(weight_path)
        self.model = CustomMobileNetV2(num_classes=2)
        custom_weights = torch.load(weight_path)
        new_state_dict = {}

        for key, value in custom_weights.items():
            # if key.startswith('classifier'):
            #     continue
            new_state_dict[key] = value

        self.model.load_state_dict(new_state_dict, strict=False)
        self.model.eval()

        self.transform = transforms.Compose([
            # transforms.ToPILImage(),
            # transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

    def preprocess(self, image: np.array):
        return self.transform(image).unsqueeze(0)

    def predict(self, image: np.array) -> int:
        transformed_image = self.preprocess(image)
        start_predict = time.time()
        outputs = self.model(transformed_image)
        print('image predice time:', time.time() - start_predict)
        predicted_class = torch.argmax(outputs, dim=1).item()
        return predicted_class


class ResNetAdapter(ModelAdapter):

    def __init__(self,
                 weight_path,
                 pretrained_model_name="microsoft/resnet-50"):
        super().__init__(weight_path)
        self.model = ResNetForImageClassification.from_pretrained(weight_path)
        #resnet는 model.eval()을 하지 않아도 되는것인지?
        self.processor = AutoImageProcessor.from_pretrained(
            pretrained_model_name)

    def preprocess(self, image: np.array):
        return self.processor(images=image, return_tensors="pt")

    def predict(self, image: np.array) -> int:
        inputs = self.preprocess(image)
        start_predict = time.time()
        outputs = self.model(**inputs)
        print('image predice time:', time.time() - start_predict)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()
        return predicted_class
