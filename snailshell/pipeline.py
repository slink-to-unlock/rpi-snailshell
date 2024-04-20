# 내장
import time
from typing import Union

# 서드파티
import cv2
import serial

# 프로젝트
from snailshell.utils.port import get_arduino_serial_ports
from snailshell.model_loader import MobileNetAdapter, ResNetAdapter


def run(
    use_pi_camera,
    video_path,
    model_name,
    weight_path,
    visualize,
    target_fps,
    arduino_port: Union[str, None],
):

    # 모델 로드
    print('모델을 로드합니다.')
    if model_name == "resnet":
        model = ResNetAdapter(weight_path)
    elif model_name == "mobilenet":
        model = MobileNetAdapter(weight_path)
    print('✅ 모델을 로드했습니다.')

    # 비디오 캡처
    if use_pi_camera:
        print('카메라를 준비합니다.')
        cap = cv2.VideoCapture(0)
    else:
        print('비디오를 준비합니다.')
        cap = cv2.VideoCapture(video_path)

    cap.set(cv2.CAP_PROP_FPS, 50)

    # 비디오의 프레임 수, 너비 및 높이 가져오기
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f'FPS:{fps}')
    print(f'FRAME_Height:{frame_height}')
    print(f'FRAME_Width:{frame_width}')
    frame_interval = int(fps / target_fps)
    frame_count = 0
    predicted_class = -1
    print('✅ 준비를 마쳤습니다.')

    # 포트 번호를 명시적으로 지정하지 않아도 모르는 기기에서 돌 수 있음
    print('아두이노 연결을 확인합니다.')
    while (port := get_arduino_serial_ports(arduino_port)) is None:
        if port:
            py_serial = serial.Serial(port, baudrate=9600)
            print('✅ 아두이노와 연결합니다.')
            break
        _t = 1
        print(f'{_t}초 뒤에 다시 시도합니다...')
        time.sleep(_t)

    while cap.isOpened():
        # 비디오로부터 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count == frame_interval:
            frame_count = 0

            # 프레임을 모델에 전달하여 클래스 예측
            predicted_class = model.predict(frame)
            py_serial.write(str(predicted_class).encode())

        if visualize:
            # 예측 클래스를 프레임에 표시
            frame = cv2.resize(frame, (500, 500))
            cv2.putText(
                frame,
                str(predicted_class),
                (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                3,
                (0, 0, 0),
                2,
            )

            # 화면에 프레임 표시
            cv2.imshow('Frame', frame)

        # 'q'를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 작업 완료 후 해제
    cap.release()

    # 모든 창 닫기
    cv2.destroyAllWindows()
