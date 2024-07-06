import unittest
import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock
from snailshell.main import parse, main


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
            download_model=True,
            wandb_project='zzangsu/AIsink-resnet50',
            wandb_artifact='model-ai-sink-run',
            without_arduino=None,
            user_id='user_1234'
        )
        args = parse()
        self.assertTrue(args.use_camera)
        self.assertEqual(args.model_name, 'model1')
        self.assertTrue(args.visualize)
        self.assertTrue(args.download_model)
        self.assertEqual(args.wandb_project, 'zzangsu/AIsink-resnet50')
        self.assertEqual(args.wandb_artifact, 'model-ai-sink-run')

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
            download_model=True,
            wandb_project='zzangsu/AIsink-resnet50',
            wandb_artifact='model-ai-sink-run',
            without_arduino=None,
            user_id='user_1234'
        )
        args = parse()
        self.assertFalse(args.use_camera)
        self.assertEqual(args.video_path, Path('snailshell/main.py'))
        self.assertEqual(args.model_name, 'model2')
        self.assertFalse(args.visualize)
        self.assertTrue(args.download_model)
        self.assertEqual(args.wandb_project, 'zzangsu/AIsink-resnet50')
        self.assertEqual(args.wandb_artifact, 'model-ai-sink-run')

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
            download_model=True,
            wandb_project='zzangsu/AIsink-resnet50',
            wandb_artifact='model-ai-sink-run',
            without_arduino=None,
            user_id='user_1234'
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
            download_model=True,
            wandb_project='zzangsu/AIsink-resnet50',
            wandb_artifact='model-ai-sink-run',
            without_arduino=None,
            user_id='user_1234'
        )
        with self.assertRaises(ValueError):
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
            download_model=True,
            wandb_project='zzangsu/AIsink-resnet50',
            wandb_artifact='model-ai-sink-run',
            without_arduino=None,
            user_id='user_1234'
        )
        with self.assertRaises(ValueError):
            parse()

    @patch('argparse.ArgumentParser.parse_args')
    @patch('os.listdir', MagicMock(return_value=[]))
    def test_exception_when_model_path_empty(self, mock_args):
        # 모델 경로에 파일이 없을 때 ValueError가 발생하는가
        mock_args.return_value = argparse.Namespace(
            use_camera=True,
            video_path=None,
            weight_path=Path('snailshell/main.py'),
            model_name='model_name',
            visualize=True,
            target_fps=30,
            picamera_module_backend=None,
            download_model=False,
            wandb_project='zzangsu/AIsink-resnet50',
            wandb_artifact='model-ai-sink-run',
            without_arduino=None,
            user_id='user_1234'
        )
        with self.assertRaises(ValueError):
            main()


if __name__ == '__main__':
    unittest.main()
