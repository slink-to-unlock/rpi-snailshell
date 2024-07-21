# 내장
import os
import time
from typing import Any, Optional
from datetime import datetime

# 서드파티
import cv2
import pytz
from discord_webhook import DiscordWebhook

# 프로젝트
from snailshell.frame_loader.base import FrameLoaderBackend
from snailshell.model_loader.resnet import ResNetAdapter
from snailshell.model_loader.mobilenet import MobileNetAdapter
from snailshell.tools.datalakeuploader import DatalakeUploader
from autosink_data_elt.log.filehandler import JSONFileHandler


class PipelineState:

    def __init__(
        self,
        started_time: datetime = None,
        frame_count: int = 0,
        magnetic_satus: Optional[int] = 1,
        predicted_class: Optional[int] = None,
    ) -> None:
        self.started_time = started_time
        self.finished_time = None
        self.frame_count = frame_count
        self.magnetic_satus = magnetic_satus
        self.predicted_class = predicted_class
        self.save_candidates = []


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
        model_version_info: str = '',
    ):
        if model_name.lower() == "mobilenet":
            model = MobileNetAdapter(weight_path)
        elif model_name.lower() == "resnet":
            model = ResNetAdapter(weight_path)
        else:
            raise ValueError("Unsupported model name. Please choose 'mobilenet' or 'resnet'.")

        self.frame_loader = frame_loader
        self.model = model
        self.model_name = model_name
        self.model_version_info = model_version_info
        self.use_arduino = use_arduino
        self.visualize = visualize
        self.target_fps = target_fps
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')
        self.user_id = user_id
        self.uploader = DatalakeUploader(user_id)

        if self.use_arduino:
            import serial
            self.serial = serial.Serial('/dev/ttyACM0', 9600)

        print(f'비디오 스트림의 프레임은 {self.frame_loader.fps}프레임입니다.')
        print(f'최대 {self.frame_interval}프레임마다 1번씩 추론을 수행합니다.')

        # 파이프라인 실시간 실행 상태. `__call__()` 에서 업데이트됨.
        self._run_state = {
            'started_time': None,
            'frame_count': 0,
            'save_candidates': [],
            'magnetic_satus': None,
            'prev_predicted_class': None,
            'predicted_class': None,
            'total_interrupt_cnt': 0,
        }

    @property
    def magnetic_status(self):
        """ 자석센서 상태
        """
        return self._run_state.get('magnetic_status')

    @magnetic_status.setter
    def magnetic_status(self, v: int):
        self._run_state.update('magnetic_status', v)

    @property
    def predicted_class(self):
        """ 이번 추론 결과
        """
        return self._run_state.get('predicted_class')

    @predicted_class.setter
    def predicted_class(self, v):
        self.prev_predicted_class = self.predicted_class
        return self._run_state.update('predicted_class', v)

    @property
    def prev_predicted_class(self):
        """ 이전 추론 결과
        """
        return self._run_state.get('prev_predicted_class')

    @prev_predicted_class.setter
    def prev_predicted_class(self, v):
        self._run_state.update('prev_predicted_class', v)

    @property
    def frame_interval(self):
        """ 추론 주기
        """
        return int(self.frame_loader.fps / self.target_fps)

    @property
    def do_inference(self):
        """ 파이프라인에서 추론 주기를 직접 계산하지 않고
        `if do_inference:` 와 같은 형태로 관리하기 위해 사용하는 멤버 변수
        """
        return self._run_state.get('frame_count') % self.frame_interval == 0

    def add_frame_count(self):
        self._run_state['frame_count'] += 1

    def notify(
        self,
        started_time: datetime,
        finished_time: datetime,
        interruption_cnt: int,
        tz: str = 'Asia/Seoul',
    ):
        """ 디스코드에 알림을 전송
        """
        assert isinstance(started_time, datetime), 'started_time must be a datetime object'
        assert isinstance(finished_time, datetime), 'finished_time must be a datetime object'
        if not self.discord_webhook_url:
            print('디스코드 웹훅 URL이 지정되지 않아 전송을 생략합니다.')
            return

        timezone = pytz.timezone(tz)
        started_time = started_time.astimezone(timezone)
        finished_time = finished_time.astimezone(timezone)
        dt = (finished_time - started_time).total_seconds() / 60

        DiscordWebhook(
            self.discord_webhook_url,
            content=(
                f'{started_time.strftime("%Y-%m-%d %H:%M:%S")}에 시작한 설거지가 **종료**되었습니다. 🎉\n'
                f'- **모델:** {self.model_name} v{self.model_version_info}\n'
                f'- **설거지 시간:** {dt:.2f}분\n'
                f'- **인터럽트 횟수:** {interruption_cnt}회\n'
            ),
            username='수전 [수전 id]',
            timeout=2,
        ).execute()

    def __call__(self) -> Any:
        self.started_time = datetime.now()

        self.predicted_class = -1

        self.frame_loader.initialize()
        self.before_loop_start()
        while True:
            frame = self.frame_loader.get_frame()
            if frame is None:
                break
            self.iteration(frame)
            self.add_frame_count()
        self.after_loop_end()

    def before_loop_start(self) -> None:
        self.extracted_data = []
        self.file_handler = JSONFileHandler(self.user_id)
        self.active_feedback_data = self.file_handler.create_default_data(
            version=2,
            deque_size=self.frame_interval,
        )

        self.previous_predicted_class = -1
        self.magnetic_status = 0
        self.passive_feedback_data = None

    def after_loop_end(self):
        self.notify(self._started_time)

    def iteration(self, frame):
        if self.do_inference:
            self.predicted_class = self.model.predict(frame)
            if self.use_arduino:
                self.serial.write(str(self.predicted_class).encode())
            self.active_feedback_data = self.file_handler.add_interaction(
                self.active_feedback_data,
                image=frame,
                model_output=predicted_class,
                magnetic_status=self.magnetic_status,
            )
            self.detect_segment_start()
            self.store_segment_data(frame)

        if self.visualize:
            self.cv2_visualize(frame, predicted_class)
            self.cv2_handle_keypress()

    def cv2_handle_keypress(self):
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            self.interaction_detected()
        elif key == ord('0'):
            self.change_magnetic_status(0)
        elif key == ord('1'):
            self.change_magnetic_status(1)
        elif key == ord('q'):
            return

    def cv2_visualize(self, frame, predicted_class):
        display_frame = cv2.resize(frame, (500, 500))
        cv2.putText(
            display_frame,
            str(predicted_class),
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            3,
            (0, 0, 0),
            2,
        )
        cv2.imshow('Frame', display_frame)

    def run(self):
        started_time = datetime.now()
        self.frame_loader.initialize()
        frame_count = 0

        # 추가 학습 데이터를 저장할 최종 list
        extracted_data = []

        # 기본 데이터 생성 (버전 2)
        file_handler = JSONFileHandler(self.user_id)
        active_feedback_data = file_handler.create_default_data(
            version=2, deque_size=self.frame_interval
        )

        predicted_class = -1
        previous_predicted_class = -1  # 초기화 추가
        magnetic_status = 1  # magnetic_status 변수 초기값
        passive_feedback_data = None  # 초기화 추가

        while True:
            frame = self.frame_loader.get_frame()
            if frame is None:
                print('리턴받은 프레임이 없습니다.')
                break

            frame_count += 1
            if frame_count == self.frame_interval:
                frame_count = 0

                previous_predicted_class = predicted_class
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

                # 현재 magnetic_status 값과 predicted_class 값을 add_interaction 함수에 전달
                active_feedback_data = file_handler.add_interaction(
                    active_feedback_data,
                    image=frame,
                    model_output=predicted_class,
                    magnetic_status=magnetic_status,
                )

                # magnetic_status이 0이고 predicted_class가 1인 구간 탐지
                if magnetic_status == 0 and predicted_class == 1 and previous_predicted_class == 0:
                    print('magnetic_status 값이 0이고 predicted_class 값이 1인 구간이 시작되었습니다.')
                    # 구간만 저장하면 되므로 list 형식인 version 1로 선언.
                    passive_feedback_data = file_handler.create_default_data(version=1)
                elif magnetic_status == 0 and predicted_class == 1 and previous_predicted_class == 1:
                    if passive_feedback_data is not None:  # None 체크 추가
                        passive_feedback_data = file_handler.add_interaction(
                            passive_feedback_data,
                            image=frame,
                            model_output=predicted_class,
                            magnetic_status=magnetic_status,
                        )
                elif magnetic_status == 0 and predicted_class == 0 and previous_predicted_class == 1:
                    if passive_feedback_data is not None:  # None 체크 추가
                        extracted_data.append(passive_feedback_data)
                        print('magnetic_status 값이 0이고 predicted_class 값이 1인 구간이 종료되었습니다.')
                    passive_feedback_data = None  # 구간 종료 후 초기화

                # 'r' 버튼 확인
                key = cv2.waitKey(1)
                if key & 0xFF == ord('r'):
                    print('interaction이 감지되었습니다.')
                    # Interaction 발동 시 데이터를 저장
                    extracted_data.append(active_feedback_data)
                    active_feedback_data = file_handler.create_default_data(
                        version=2, deque_size=self.frame_interval
                    )

                    # predicted_class = 1 추가
                    predicted_class = 1
                    if self.use_arduino:
                        self.serial.write(str(predicted_class).encode())

                    # 3초 동안 지연
                    time.sleep(3)

                if key & 0xFF == ord('0'):
                    magnetic_status = 0
                    if predicted_class == 1:
                        extracted_data.append(active_feedback_data)
                        active_feedback_data = file_handler.create_default_data(
                            version=2, deque_size=self.frame_interval
                        )
                    print('magnetic_status 값이 0으로 변경되었습니다.')

                if key & 0xFF == ord('1'):
                    magnetic_status = 1
                    print('magnetic_status 값이 1으로 변경되었습니다.')

                if key & 0xFF == ord('q'):
                    break

        self.frame_loader.release()
        cv2.destroyAllWindows()
        finished_time = datetime.now()
        self.notify(started_time, finished_time, 1000)

        if extracted_data:
            self.uploader.save_data_and_images(extracted_data)
