# 프로젝트
from snailshell.frame_loader.base import FrameLoaderBackend


class PiCameraBackend(FrameLoaderBackend):

    def __init__(self):
        from picamera import PiCamera
        from picamera.array import PiRGBArray
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 50
        self.raw_capture = PiRGBArray(self.camera, size=(640, 480))
        self.stream = self.camera.capture_continuous(
            self.raw_capture,
            format="bgr",
            use_video_port=True,
        )

    @property
    def fps(self):
        return self.camera.framerate

    def initialize(self):
        import time
        time.sleep(0.1)  # 카메라 워밍업

    def get_frame(self):
        for frame in self.stream:
            image = frame.array
            self.raw_capture.truncate(0)
            return image

    def release(self):
        self.camera.close()
