# 서드파티
import cv2

# 프로젝트
from snailshell.frame_loader.base import FrameLoaderBackend


class OpenCVBackend(FrameLoaderBackend):

    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FPS, 50)

    @property
    def fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS)

    def initialize(self):
        pass

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()
