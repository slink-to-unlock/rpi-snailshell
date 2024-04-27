# 내장
import unittest
import argparse
from pathlib import Path
from unittest.mock import patch

# 프로젝트
from snailshell.main import parse


class TestArgumentParsing(unittest.TestCase):

    @patch('argparse.ArgumentParser.parse_args')
    def test_normal_execution_with_camera(self, mock_args):
        # 카메라 사용 정상 사용 케이스
        mock_args.return_value = argparse.Namespace(
            use_camera=True,
            video_path=None,
            weight_path=Path('snailshell/main.py'),
            model_name='model1',
            visualize=True,
            target_fps=None,
            picamera_module_backend=None,
        )
        args = parse()
        self.assertTrue(args.use_camera)
        self.assertEqual(args.model_name, 'model1')
        self.assertTrue(args.visualize)

    @patch('argparse.ArgumentParser.parse_args')
    def test_normal_execution_with_video_path(self, mock_args):
        # 비디오 경로 사용 정상 사용 케이스
        mock_args.return_value = argparse.Namespace(
            use_camera=False,
            video_path=Path('snailshell/main.py'),
            weight_path=Path('snailshell/main.py'),
            model_name='model2',
            visualize=False,
            target_fps=None,
            picamera_module_backend=None,
        )
        args = parse()
        self.assertFalse(args.use_camera)
        self.assertEqual(args.video_path, Path('snailshell/main.py'))
        self.assertEqual(args.model_name, 'model2')
        self.assertFalse(args.visualize)

    @patch('argparse.ArgumentParser.parse_args')
    def test_exception_without_video_path(self, mock_args):
        # 카메라를 사용하지 않는 경우 비디오 경로가 없을 때 ValueError가 발생하는가
        mock_args.return_value = argparse.Namespace(
            use_camera=False,
            video_path=None,
            weight_path=Path('snailshell/main.py'),
            model_name='model3',
            visualize=True,
            target_fps=None,
            picamera_module_backend=None,
        )
        with self.assertRaises(ValueError):
            parse()

    @patch('argparse.ArgumentParser.parse_args')
    def test_exception_with_fps_less_than_one(self, mock_args):
        # target_fps 가 1 이하일 경우 ValueError가 발생하는가
        mock_args.return_value = argparse.Namespace(
            use_camera=False,
            video_path=Path('snailshell/main.py'),
            weight_path=Path('snailshell/main.py'),
            model_name='model_name',
            visualize=True,
            target_fps=0,
            picamera_module_backend=None,
        )
        with self.assertRaises(ValueError):
            parse()

    @patch('argparse.ArgumentParser.parse_args')
    def test_exception_with_nonexistent_weight_path(self, mock_args):
        # 가중치 파일 경로가 잘못된 경로일 때 FileNotFoundError 가 발생하는가
        mock_args.return_value = argparse.Namespace(
            use_camera=False,
            video_path=Path('snailshell/main.py'),
            weight_path=Path('nonexistent/path/to/weights.pth'),
            model_name='model_name',
            visualize=True,
            target_fps=30,
            picamera_module_backend=None,
        )
        with self.assertRaises(FileNotFoundError):
            parse()

    @patch('argparse.ArgumentParser.parse_args')
    def test_exception_when_picamera_module_without_camera(self, mock_args):
        # picamera_module_backend가 True이고 카메라 사용이 False일 때 ValueError 테스트
        mock_args.return_value = argparse.Namespace(
            use_camera=False,
            video_path=Path('snailshell/main.py'),
            weight_path=Path('snailshell/main.py'),
            model_name='model_name',
            visualize=True,
            target_fps=30,
            picamera_module_backend=True,
        )
        with self.assertRaises(ValueError):
            parse()


if __name__ == '__main__':
    unittest.main()
