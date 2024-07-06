import os
import argparse
import logging
from snailshell.pipelines.base import BasePipeline
from snailshell.frame_loader.opencv_backend import OpenCVBackend
from snailshell.frame_loader.picamera_backend import PiCameraBackend
from snailshell.tools.modeldownloader import ModelDownloader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


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
        help='모델 가중치 파일 경로. 지정하지 않으면, 모델을 다운로드 하는 경우 기본 경로를 사용합니다.',
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
        help='`picamera` 모듈을 사용하도록 합니다. 지정하지 않으면 opencv 백엔드를 사용합니다.',
    )
    parser.add_argument(
        '--without_arduino',
        action='store_true',
        help='아두이노 없이도 프로그램을 실행할 수 있습니다. 이 옵션을 사용하면 아두이노 관련 기능이 비활성화됩니다.',
    )
    parser.add_argument(
        '--wandb_project',
        type=str,
        help='최신 모델이 저장되어 있는 wandb의 project이름을 입력합니다. 모델 다운로드를 수행하려면 필수입니다.',
        default="zzangsu/AIsink-resnet50",
    )
    parser.add_argument(
        '--wandb_artifact',
        type=str,
        help='최신 모델이 저장되어 있는 wandb의 project속 artifact 이름을 입력합니다. 모델 다운로드를 수행하려면 필수입니다.',
        default="model-ai-sink-run",
    )
    parser.add_argument(
        '--download_model',
        action='store_true',
        help='모델 다운로드 수행 여부. 지정하면 모델을 다운로드하고, 지정하지 않으면 기존 모델 가중치 파일을 사용합니다.',
    )
    parser.add_argument(
        '--user_id',
        type=str,
        help='user id를 입력합니다.',
        default="user_1234",
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

    # 파이카메라 모듈을 사용하고자 하는 경우, 반드시 카메라를 사용해야 함
    if args.picamera_module_backend:
        if not args.use_camera:
            raise ValueError('`picamera` 모듈 백엔드를 사용하고자 하는 경우 반드시 카메라를 사용해야 합니다.')

    # 모델 다운로드 시 wandb 정보가 필요
    if args.download_model:
        if not args.wandb_project or not args.wandb_artifact:
            raise ValueError('모델 다운로드를 수행하려면 `--wandb_project` 및 `--wandb_artifact` 를 지정해야 합니다.')
        if not args.weight_path:
            args.weight_path = os.path.join('.', '.cache')
    else:
        if not args.weight_path:
            raise ValueError('모델 경로를 지정해야 합니다.')

    return args


def main():
    args = parse()

    if args.download_model:
        model_updater = ModelDownloader(
            project_name=args.wandb_project,
            artifact_name=args.wandb_artifact,
            aliases=['latest', 'success'],
            base_model_path=args.weight_path,
            api_key=os.getenv('WANDB_API_KEY')
        )
        model_updater.update_model()
        logging.info('모델 업데이트가 완료되었습니다.')
    else:
        if not os.listdir(args.weight_path):
            raise ValueError('모델 경로에 모델 파일이 없습니다. 모델 다운로드가 필요합니다.')
        logging.info('모델 업데이트를 건너뜁니다.')

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
        user_id=args.user_id,
    )
    pipeline.run()


if __name__ == '__main__':
    main()
