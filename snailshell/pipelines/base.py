import cv2
from collections import deque
from datetime import datetime

# 프로젝트
from snailshell.frame_loader.base import FrameLoaderBackend
from snailshell.model_loader.resnet import ResNetAdapter
from snailshell.model_loader.mobilenet import MobileNetAdapter
from snailshell.tools.uploadlake import UploadLake


class BasePipeline:

    def __init__(
        self,
        frame_loader: FrameLoaderBackend,
        model_name: str,
        weight_path: str,
        use_arduino=False,
        visualize=False,
        target_fps=10,
        # user_id='user_1234',  # 추가: user_id 인자
    ):
        if model_name.lower() == "mobilenet":
            model = MobileNetAdapter(weight_path)
        elif model_name.lower() == "resnet":
            model = ResNetAdapter(weight_path)
        else:
            raise ValueError(
                "Unsupported model name. Please choose 'mobilenet' or 'resnet'."
            )

        self.frame_loader = frame_loader
        self.model = model
        self.use_arduino = use_arduino
        self.visualize = visualize
        self.target_fps = target_fps
        self.dishwashing_start = datetime.now().strftime("%Y%m%d")
        self.interaction_counter = 1

        user_id = 'user_1234'  # 함수 인자 수정 전 임시 user_id 변수 생성.
        self.uploader = UploadLake(user_id)  # 추가: UploadLake 인스턴스 초기화

        if self.use_arduino:
            import serial
            self.serial = serial.Serial('/dev/ttyACM0', 9600)

        print(f'비디오 스트림의 프레임은 {self.frame_loader.fps}프레임입니다.')
        print(f'최대 {self.frame_interval}프레임마다 1번씩 추론을 수행합니다.')

    @property
    def frame_interval(self):
        return int(self.frame_loader.fps / self.target_fps)

    def run(self):
        self.frame_loader.initialize()
        frame_count = 0
        save_sec = 3  # interrupt가 입력되면 이전 save_sec 초의 프레임을 저장.

        # 추가 학습 데이터를 저장할 최종 list
        extracted_data = {}
        # 이미지와 라벨을 임시로 저장할 list
        run_images = deque(maxlen=self.frame_interval * save_sec)
        run_labels = deque(maxlen=self.frame_interval * save_sec)
        timestamps = deque(maxlen=self.frame_interval * save_sec)

        predicted_class = -1

        while True:
            frame = self.frame_loader.get_frame()
            if frame is None:
                print('리턴받은 프레임이 없습니다.')
                break

            frame_count += 1
            if frame_count == self.frame_interval:
                frame_count = 0

                predicted_class = self.model.predict(frame)
                if self.use_arduino:
                    self.serial.write(str(predicted_class).encode())

                if self.visualize:
                    display_frame = cv2.resize(frame, (500, 500))
                    cv2.putText(
                        display_frame,
                        text=str(predicted_class),
                        org=(50, 100),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=3,
                        color=(0, 0, 0),
                        thickness=2,
                    )
                    cv2.imshow('Frame', display_frame)

            # 이미지와 라벨을 저장할 deque에 추가
            run_images.append(frame)
            run_labels.append(predicted_class)

            # 'r' 버튼 확인
            key = cv2.waitKey(1)
            if key & 0xFF == ord('r'):
                print('interaction이 감지되었습니다.')
                # list에 들어 있는 이미지를 JSONFileHandler class의 add_interaction 형태로 가공. 그러나 이미지를 다운로드하거나

            if key & 0xFF == ord('q'):
                break

        if upload_imgdata:
            self.uploader.save_data_and_images(
                extracted_data, list(run_images))  # 수정: 호출 메소드 변경

        self.frame_loader.release()
        cv2.destroyAllWindows()
