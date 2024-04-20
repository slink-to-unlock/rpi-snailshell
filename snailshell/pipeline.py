# 서드파티
import cv2
import serial
import time

# 프로젝트
from snailshell.model_loader import MobileNetAdapter, ResNetAdapter


def run(
    use_pi_camera,
    video_path,
    model_name,
    weight_path,
    visualize,
    target_fps,
    use_arduino,
):
    if use_arduino:
        py_serial = serial.Serial('/dev/ttyACM0', 9600)

    print('모델을 로드합니다.')
    if model_name == "resnet":
        model = ResNetAdapter(weight_path)
    elif model_name == "mobilenet":
        model = MobileNetAdapter(weight_path)

    # 비디오 캡처
    if use_pi_camera:
        print('라즈베리파이 카메라를 사용합니다.')
        cap = cv2.VideoCapture(0)
    else:
        print(f'비디오 `{video_path}` 를 사용합니다.')
        cap = cv2.VideoCapture(video_path)

    cap.set(cv2.CAP_PROP_FPS, 50)
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
            print('리턴받은 프레임이 없습니다.')
            break

        frame_count += 1
        if frame_count == frame_interval:
            frame_count = 0

            # 프레임을 모델에 전달하여 클래스 예측
            predicted_class = model.predict(frame)

            if use_arduino:
                py_serial.write(str(predicted_class).encode())

        if visualize:
            # 예측 클래스를 프레임에 표시
            frame = cv2.resize(frame, (500, 500))
            cv2.putText(
                frame,
                text=str(predicted_class),
                org=(50, 100),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=3,
                color=(0, 0, 0),
                thickness=2,
            )

            # 화면에 프레임 표시
            cv2.imshow('Frame', frame)

        # 'q'를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print('작업을 마치고 프로세스를 종료합니다.')
    cap.release()
    cv2.destroyAllWindows()
