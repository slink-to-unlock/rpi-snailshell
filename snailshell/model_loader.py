import torch
import torch.nn as nn
import numpy as np
from PIL import Image
from torchvision import models
from torchvision import transforms
import torchvision.transforms as transforms
from transformers import ResNetForImageClassification, AutoImageProcessor
from snailshell.model_class import CustomMobileNetV2
from torchsummary import summary


def model_loader(model_name: str, weight_path: str):

    if model_name == "mobilenet":  #Mobilenet 모델일 경우
        model = CustomMobileNetV2(num_classes=2)
        custom_weights = torch.load(weight_path)
        new_state_dict = {}

        for key, value in custom_weights.items():
            # if key.startswith('classifier'):
            #     continue
            new_state_dict[key] = value

        model.load_state_dict(new_state_dict, strict=False)

        model.eval()

        return model

    elif model_name == "resnet":  #resnet-50 모델일 경우
        model = ResNetForImageClassification.from_pretrained(weight_path)

        return model


def do_inferance(image: np.array, model, model_name: str) -> int:
    if model_name == "mobilenet":
        transform_MobileNet_V2 = transforms.Compose([
            # transforms.ToPILImage(),
            # transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

        # 전처리
        transformed_image = transform_MobileNet_V2(image)

        # 모델에 입력하기 위해 차원 추가
        transformed_image = transformed_image.unsqueeze(0)

        outputs = model(transformed_image)

        # 예측된 클래스 인덱스 찾기
        predicted_class = torch.argmax(outputs, dim=1).item()

        return predicted_class

    elif model_name == "resnet":
        #processor 선언
        pretrained_model_name = "microsoft/resnet-50"
        processor = AutoImageProcessor.from_pretrained(pretrained_model_name)

        #images: np.array의 형태. 입력값 예측.
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()

        #예측 label 반환
        return predicted_class


model_name = "mobilenet"
weight_path = "examples/mobilenet_v2-7ebf99e0.pth"
image_path = "examples/test_image.jpg"
model = model_loader(model_name, weight_path)
summary(model.eval(), (3, 224, 224))
img = Image.open(image_path)
img_array = np.array(img)
print(do_inferance(img_array, model, model_name))
