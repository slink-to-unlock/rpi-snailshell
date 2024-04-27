# 내장
from abc import ABC, abstractmethod

# 서드파티
import numpy as np


class ModelAdapter(ABC):

    def __init__(self, weight_path):
        self.weight_path = weight_path

    @abstractmethod
    def preprocess(
        self,
        image: np.array,
    ):
        pass

    @abstractmethod
    def predict(
        self,
        image: np.array,
    ) -> int:
        pass
