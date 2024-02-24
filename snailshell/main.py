""" 사용예시
- python3 -m snailshell.main.py --model your_model_name
- python3 -m snailshell.main.py --video_path /path/to/video.mp4 --model your_model_name --visualize`
"""
# 내장
import argparse

# 프로젝트
from snailshell import pipeline


def parse():
    parser = argparse.ArgumentParser(description='런타임 애플리케이션')
    parser.add_argument(
        '--use_pi_camera',
        action='store_true',
        default=True,
        help='라즈베리파이 카메라 사용',
    )
    parser.add_argument(
        '--video_path',
        type=str,
        help='라즈베리파이 카메라를 사용하지 않는 경우 입력하는 비디오파일의 경로',
        default='',
    )
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='사용할 모델의 이름',
    )
    parser.add_argument(
        '--visualize',
        action='store_true',
        default=True,
        help='시각화 수행 여부',
    )
    # 프레임 수를 처리하기 위한 새로운 인자 추가
    parser.add_argument(
        '--fps',
        type=int,
        help='최대 초당 프레임 처리량. 단, 이 값이 높아도 실제 처리량은 하드웨어 성능에 의존적입니다.',
        default=None,
    )

    args = parser.parse_args()

    # 라즈베리파이 카메라를 사용하지 않을 경우 비디오 경로가 필수
    if not args.use_pi_camera and not args.video_path:
        raise ValueError('카메라를 사용하지 않는 경우 `--video_path` 가 필수적입니다.')

    # 프레임 수가 제공되었는지 확인 (선택적)
    if args.fps is not None and args.fps < 1:
        raise ValueError('`--fps` 값은 1 이상의 정수여야 합니다.')

    return args


if __name__ == '__main__':
    args = parse()
    pipeline.run(
        use_pi_camera=args.use_pi_camera,
        video_path=args.video_path,
        model=args.model,
        visualize=args.visualize,
        fps=args.fps,
    )
