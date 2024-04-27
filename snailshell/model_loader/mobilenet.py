# 내장
import time

# 서드파티
import torch
import numpy as np
from torchvision import transforms
import torchvision.transforms as transforms

# 프로젝트
from snailshell.adapters.base import ModelAdapter
from snailshell.models.mobilenet import CustomMobileNetV2


class MobileNetAdapter(ModelAdapter):
    # class를 선언할 때 weight_path를 입력받아 모델과 전처리기 한번만 선언 후 함수를 통해 예측.
    def __init__(
        self,
        weight_path,
    ):
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

        self.transform = transforms.Compose(
            [
                # transforms.ToPILImage(),
                # transforms.Resize((224, 224)),
                transforms.ToTensor()
            ]
        )

    def preprocess(
        self,
        image: np.array,
    ):
        return self.transform(image).unsqueeze(0)

    def predict(self, image: np.array) -> int:
        transformed_image = self.preprocess(image)
        # print(f'input: (type: {type(transformed_image)}) {transformed_image}')
        # start_predict = time.time()
        outputs = self.model(transformed_image)
        # print('image predice time:', time.time() - start_predict)
        print('🧐 [0, 1]:', torch.softmax(outputs, dim=-1))
        predicted_class = torch.argmax(outputs, dim=1).item()
        return predicted_class
