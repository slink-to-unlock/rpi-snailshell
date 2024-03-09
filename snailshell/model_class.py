import torch.nn as nn
from torchvision import models


#MobileNet 모델 class 선언
class CustomMobileNetV2(nn.Module):

    def __init__(self, num_classes=2):
        super(CustomMobileNetV2, self).__init__()

        model_pretrained = models.mobilenet_v2()

        for param in model_pretrained.parameters():
            param.requires_grad = False

        # model_pretrained.classifier[0].requires_grad = False
        # model_pretrained.classifier[1] = nn.Linear(in_features=1280,
        #                                            out_features=num_classes)
        model_pretrained.classifier = nn.Linear(in_features=1280,
                                                out_features=num_classes)
        self.features = model_pretrained.features
        self.classifier = model_pretrained.classifier

    def forward(self, x):
        x = self.features(x)
        x = x.mean([2, 3])
        x = self.classifier(x)
        return x
