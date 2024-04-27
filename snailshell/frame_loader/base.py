# 내장
from abc import ABC, abstractmethod


class FrameLoaderBackend(ABC):

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def get_frame(self):
        pass

    @abstractmethod
    def release(self):
        pass

    @property
    @abstractmethod
    def fps(self):
        pass
