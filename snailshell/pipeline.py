# 서드파티
import cv2
import serial
import time

# 프로젝트
from snailshell.model_loader import MobileNetAdapter, ResNetAdapter

py_serial = serial.Serial(
    '/dev/ttyACM0',
    9600,
)


def run(
    use_pi_camera,
    video_path,
    model_name,
    weight_path,
    visualize,
    target_fps,
):

    # 모델 로드
    if model_name == "resnet":
        model = ResNetAdapter(weight_path)
    elif model_name == "mobilenet":
        model = MobileNetAdapter(weight_path)

    # 비디오 캡처
    if use_pi_camera:
        cap = cv2.VideoCapture(0)
    else:
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
            cv2.putText(frame, str(predicted_class), (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 2)

            # 화면에 프레임 표시
            cv2.imshow('Frame', frame)

        # 'q'를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 작업 완료 후 해제
    cap.release()

    # 모든 창 닫기
    cv2.destroyAllWindows()
