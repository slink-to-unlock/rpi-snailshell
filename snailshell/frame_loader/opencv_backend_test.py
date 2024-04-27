# 내장
import unittest

# 프로젝트
from snailshell.frame_loader.opencv_backend import OpenCVBackend


class TestOpenCVBackend(unittest.TestCase):

    def setUp(self):
        # 테스트 전에 실행되는 코드
        self.backend = None

    def test_get_frame_from_file(self):
        # 실제 파일에서 프레임을 로드하는 경우를 테스트
        self.backend = OpenCVBackend('examples/test_video.mov')
        frame = self.backend.get_frame()

        # 프레임이 정상적으로 로드되었는지 확인
        self.assertIsNotNone(frame)
        self.assertTrue(frame.any())  # ndarray가 비어있지 않은지 확인
        self.assertEqual(self.backend.fps, 50)

    def test_get_frame_from_camera(self):
        # 카메라 인덱스를 통해 프레임을 로드하는 경우를 테스트
        self.backend = OpenCVBackend(0)
        frame = self.backend.get_frame()

        # 프레임이 정상적으로 로드되었는지 확인
        self.assertIsNotNone(frame)
        self.assertTrue(frame.any())  # ndarray가 비어있지 않은지 확인
        self.assertEqual(self.backend.fps, 50)

    def tearDown(self):
        # 테스트 후 정리 코드
        if self.backend:
            self.backend.release()


if __name__ == '__main__':
    unittest.main()
