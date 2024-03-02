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
        # 라즈베리파이 카메라 사용 정상 사용 케이스
        mock_args.return_value = argparse.Namespace(
            use_pi_camera=True,
            video_path=None,
            weight_path=Path('snailshell/main.py'),
            model_name='model1',
            visualize=True,
            target_fps=None,
        )
        args = parse()
        self.assertTrue(args.use_pi_camera)
        self.assertEqual(args.model_name, 'model1')
        self.assertTrue(args.visualize)

    @patch('argparse.ArgumentParser.parse_args')
    def test_normal_execution_with_video_path(self, mock_args):
        # 비디오 경로 사용 정상 사용 케이스
        mock_args.return_value = argparse.Namespace(
            use_pi_camera=False,
            video_path=Path('snailshell/main.py'),
            weight_path=Path('snailshell/main.py'),
            model_name='model2',
            visualize=False,
            target_fps=None,
        )
        args = parse()
        self.assertFalse(args.use_pi_camera)
        self.assertEqual(args.video_path, Path('snailshell/main.py'))
        self.assertEqual(args.model_name, 'model2')
        self.assertFalse(args.visualize)

    @patch('argparse.ArgumentParser.parse_args')
    def test_exception_without_video_path(self, mock_args):
        # 카메라를 사용하지 않는 경우 비디오 경로가 없을 때 ValueError가 발생하는가
        mock_args.return_value = argparse.Namespace(
            use_pi_camera=False,
            video_path=None,
            weight_path=Path('snailshell/main.py'),
            model_name='model3',
            visualize=True,
            target_fps=None,
        )
        with self.assertRaises(ValueError):
            parse()

    @patch('argparse.ArgumentParser.parse_args')
    def test_exception_with_fps_less_than_one(self, mock_args):
        # target_fps 가 1 이하일 경우 ValueError가 발생하는가
        mock_args.return_value = argparse.Namespace(
            use_pi_camera=False,
            video_path=Path('snailshell/main.py'),
            weight_path=Path('snailshell/main.py'),
            model_name='model_name',
            visualize=True,
            target_fps=0,
        )
        with self.assertRaises(ValueError):
            parse()

    @patch('argparse.ArgumentParser.parse_args')
    def test_exception_with_nonexistent_weight_path(self, mock_args):
        # 가중치 파일 경로가 잘못된 경로일 때 FileNotFoundError 가 발생하는가
        mock_args.return_value = argparse.Namespace(
            use_pi_camera=False,
            video_path=Path('snailshell/main.py'),
            weight_path=Path('nonexistent/path/to/weights.pth'),
            model_name='model_name',
            visualize=True,
            target_fps=30,
        )
        with self.assertRaises(FileNotFoundError):
            parse()


if __name__ == '__main__':
    unittest.main()
