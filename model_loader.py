from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.init as init

import torchvision
from torchvision import models
from torchvision import transforms
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2

class CustomMobileNetV2(nn.Module):
    def __init__(self, num_classes=2):
        super(CustomMobileNetV2, self).__init__()

        model_pretrained = models.mobilenet_v2(pretrained=True)

        for param in model_pretrained.parameters():
            param.requires_grad = False

        model_pretrained.classifier[0].requires_grad = True
        model_pretrained.classifier[1] = nn.Linear(in_features=1280, out_features=num_classes)
        self.features = model_pretrained.features
        self.classifier = model_pretrained.classifier

    def forward(self, x):
        x = self.features(x)
        x = x.mean([2, 3])
        x = self.classifier(x)
        return x


transform_MobileNet_V2 = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])


model = CustomMobileNetV2(num_classes=2)
custom_weights = torch.load('/Users/sukcess/Documents/WorkSpace/sink/mobilenet_v2-7ebf99e0.pth')
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
image_path = 'examples/test_image.jpg'
def pridictImage (image_path):
    val_image = Image.open(image_path)
    val_image = transform_MobileNet_V2(val_image)
    val_image = val_image.unsqueeze(0)

    val_outputs = model(val_image)

    val_predicted_class_idx = torch.argmax(val_outputs, dim=1).item()

    print(f"Pridict label: {val_predicted_class_idx}")

pridictImage(image_path)
