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
from snailshell import pipeline


def parse():
    parser = argparse.ArgumentParser(description='런타임 애플리케이션')
    parser.add_argument(
        '--use_pi_camera',
        action='store_true',
        help='라즈베리파이 카메라 사용',
    )
    parser.add_argument(
        '--video_path',
        type=str,
        help='라즈베리파이 카메라를 사용하지 않는 경우 입력하는 비디오파일의 경로',
        default='',
    )
    parser.add_argument(
        '--model_name',
        type=str,
        required=True,
        help='사용할 모델의 이름: modilenet, resnet',
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
    # 프레임 수를 처리하기 위한 새로운 인자 추가
    parser.add_argument(
        '--target_fps',
        type=int,
        help='최대 초당 프레임 처리량. 단, 이 값이 높아도 실제 처리량은 하드웨어 성능에 의존적입니다.',
        default=10,
    )

    args = parser.parse_args()

    # 라즈베리파이 카메라를 사용하지 않을 경우 비디오 경로가 필수
    if not args.use_pi_camera:
        if not args.video_path:
            raise ValueError('카메라를 사용하지 않는 경우 `--video_path` 가 필수적입니다.')
        elif not os.path.exists(args.video_path):
            raise FileNotFoundError(f"{args.video_path} 파일을 찾을 수 없습니다.")

    # 프레임 수가 제공되었는지 확인 (선택적)
    if args.target_fps is not None and args.target_fps < 1:
        raise ValueError('`--target_fps` 값은 1 이상의 정수여야 합니다.')

    if not os.path.exists(args.weight_path):
        raise FileNotFoundError(f"{args.weight_path} 파일이나 디렉토리를 찾을 수 없습니다.")

    return args


if __name__ == '__main__':
    args = parse()
    pipeline.run(
        use_pi_camera=args.use_pi_camera,
        video_path=args.video_path,
        weight_path=args.weight_path,
        model_name=args.model_name,
        visualize=args.visualize,
        target_fps=args.target_fps,
    )
