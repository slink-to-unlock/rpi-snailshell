""" 사용예시
python3 -m snailshell.main \
    --model_name your_model_name \
    --weight_path /path/to/weights

python3 -m snailshell.main \
    --video_path /path/to/video.mp4 \
    --model_name your_model_name \
    --visualize \
    --weight_path /path/to/weights
"""
# 내장
import os
import argparse

# 프로젝트
from snailshell.pipelines.base import BasePipeline
from snailshell.frame_loader.opencv_backend import OpenCVBackend
from snailshell.frame_loader.picamera_backend import PiCameraBackend


def parse():
    parser = argparse.ArgumentParser(description='런타임 애플리케이션')
    parser.add_argument(
        '--use_camera',
        action='store_true',
        help='카메라 사용',
    )
    parser.add_argument(
        '--video_path',
        type=str,
        help='카메라를 사용하지 않는 경우 입력하는 비디오파일의 경로',
        default='',
    )
    parser.add_argument(
        '--model_name',
        type=str,
        required=True,
        help='사용할 모델의 이름: mobilenet, resnet',
    )
    parser.add_argument(
        '--weight_path',
        type=str,
        required=True,
        help='모델 가중치 파일 경로',
    )
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='시각화 수행 여부',
    )
    parser.add_argument(
        '--target_fps',
        type=int,
        help='최대 초당 프레임 처리량. 단, 이 값이 높아도 실제 처리량은 하드웨어 성능에 의존적입니다.',
        default=10,
    )
    parser.add_argument(
        '--picamera_module_backend',
        action='store_true',
        help='`picamera` 모듈을 사용하도록 합니다.',
    )
    parser.add_argument(
        '--without_arduino',
        action='store_true',
        help='아두이노 없이도 프로그램을 실행할 수 있습니다. 이 옵션을 사용하면 아두이노 관련 기능이 비활성화됩니다.',
    )
    args = parser.parse_args()

    # 라즈베리파이 카메라를 사용하지 않을 경우 비디오 경로가 필수
    if not args.use_camera:
        if not args.video_path:
            raise ValueError('카메라를 사용하지 않는 경우 `--video_path` 가 필수적입니다.')
        elif not os.path.exists(args.video_path):
            raise FileNotFoundError(f"{args.video_path} 파일을 찾을 수 없습니다.")

    # 프레임 수가 제공되었는지 확인 (선택적)
    if args.target_fps is not None and args.target_fps < 1:
        raise ValueError('`--target_fps` 값은 1 이상의 정수여야 합니다.')
    if not os.path.exists(args.weight_path):
        raise FileNotFoundError(f"{args.weight_path} 파일이나 디렉토리를 찾을 수 없습니다.")

    # 파이카메라 모듈을 사용하고자 하는 경우, 반드시 카메라를 사용해야 함
    if args.picamera_module_backend:
        if not args.use_camera:
            raise ValueError('`picamera` 모듈 백엔드를 사용하고자 하는 경우 반드시 카메라를 사용해야 합니다.')

    return args


def main():
    args = parse()

    # 백엔드 선택
    if args.picamera_module_backend:
        backend = PiCameraBackend()
    else:
        if args.use_camera:
            backend = OpenCVBackend(0)
        else:
            backend = OpenCVBackend(args.video_path)

    # 파이프라인 설정 및 실행
    pipeline = BasePipeline(
        frame_loader=backend,
        model_name=args.model_name,
        weight_path=args.weight_path,
        use_arduino=not args.without_arduino,
        visualize=args.visualize,
        target_fps=args.target_fps,
    )
    pipeline.run()


if __name__ == '__main__':
    main()
