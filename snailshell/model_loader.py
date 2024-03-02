import torch
import torch.nn as nn
import numpy as np
from PIL import Image
from torchvision import models
from torchvision import transforms
import torchvision.transforms as transforms
from transformers import ResNetForImageClassification, AutoImageProcessor


#MobileNet 모델 class 선언
class CustomMobileNetV2(nn.Module):

    def __init__(self, num_classes=2):
        super(CustomMobileNetV2, self).__init__()

        model_pretrained = models.mobilenet_v2(pretrained=True)

        for param in model_pretrained.parameters():
            param.requires_grad = False

        model_pretrained.classifier[0].requires_grad = True
        model_pretrained.classifier[1] = nn.Linear(in_features=1280,
                                                   out_features=num_classes)
        self.features = model_pretrained.features
        self.classifier = model_pretrained.classifier

    def forward(self, x):
        x = self.features(x)
        x = x.mean([2, 3])
        x = self.classifier(x)
        return x


def model_loader(model_name: str, weight_path: str):

    if model_name == "mobilenet":
        model = CustomMobileNetV2(num_classes=2)
        custom_weights = torch.load(weight_path)
        new_state_dict = {}

        for key, value in custom_weights.items():
            if key.startswith('classifier'):
                continue
            new_state_dict[key] = value

        model.load_state_dict(new_state_dict, strict=False)

        in_features = model.classifier[1].in_features
        model.classifier[1] = torch.nn.Linear(in_features, 2)

        for param in model.features.parameters():
            param.requires_grad = False

        model.eval()

        return model

    elif model_name == "resnet":
        model_name = weight_path
        model = ResNetForImageClassification.from_pretrained(model_name)

        return model


def do_inferance(image: np.array, model, model_name: str) -> int:
    if model_name == "mobilenet":
        transform_MobileNet_V2 = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

        # 전처리
        transformed_image = transform_MobileNet_V2(image)

        # 모델에 입력하기 위해 차원 추가
        transformed_image = transformed_image.unsqueeze(0)

        predicted_class = model(transformed_image)

        # 예측된 클래스 인덱스 찾기
        predicted_class_idx = torch.argmax(predicted_class, dim=1).item()

        return predicted_class_idx

    elif model_name == "resnet":
        pretrained_model_name = "microsoft/resnet-50"
        processor = AutoImageProcessor.from_pretrained(pretrained_model_name)
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()
        return predicted_class
