import cv2

# 프로젝트
from snailshell.frame_loader.base import FrameLoaderBackend
from snailshell.model_loader.resnet import ResNetAdapter
from snailshell.model_loader.mobilenet import MobileNetAdapter
from snailshell.tools.datalakeuploader import DatalakeUploader
from autosink_data_elt.log.filehandler import JSONFileHandler


class BasePipeline:

    def __init__(
        self,
        frame_loader: FrameLoaderBackend,
        model_name: str,
        weight_path: str,
        user_id: str,
        use_arduino=False,
        visualize=False,
        target_fps=10,
    ):
        if model_name.lower() == "mobilenet":
            model = MobileNetAdapter(weight_path)
        elif model_name.lower() == "resnet":
            model = ResNetAdapter(weight_path)
        else:
            raise ValueError("Unsupported model name. Please choose 'mobilenet' or 'resnet'.")

        self.frame_loader = frame_loader
        self.model = model
        self.use_arduino = use_arduino
        self.visualize = visualize
        self.target_fps = target_fps
        self.user_id = user_id
        self.uploader = DatalakeUploader(user_id)

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

        # 추가 학습 데이터를 저장할 최종 list
        extracted_data = []

        # 기본 데이터 생성 (버전 2)
        file_handler = JSONFileHandler(self.user_id)
        data = file_handler.create_default_data(version=2, deque_size=self.frame_interval)

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

            data = file_handler.add_interaction(data, image=frame, model_output=predicted_class)

            # 'r' 버튼 확인
            key = cv2.waitKey(1)
            if key & 0xFF == ord('r'):
                print('interaction이 감지되었습니다.')
                # Interaction 발동 시 데이터를 저장
                extracted_data.append(data)
                data = file_handler.create_default_data(version=2, deque_size=self.frame_interval)

            if key & 0xFF == ord('q'):
                break

        self.frame_loader.release()
        cv2.destroyAllWindows()

        if extracted_data:
            self.uploader.save_data_and_images(extracted_data)
