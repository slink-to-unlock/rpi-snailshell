import cv2
from model_loader import model_loader, do_inference

# 비디오 파일 경로
video_path = 'example_video/dog_example.mp4'

# 모델 로드
model = model_loader()

# 비디오 캡처
cap = cv2.VideoCapture(video_path)

# 비디오의 프레임 수, 너비 및 높이 가져오기
fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(fps)
print(frame_height)
print(frame_width)
frame_interval = 10
frame_count = 0
predicted_class = -1
while cap.isOpened():
    # 비디오로부터 프레임 읽기
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (400, 600))
    frame_count += 1
    if frame_count == frame_interval:
        frame_count = 0

        # 프레임을 모델에 전달하여 클래스 예측
        predicted_class = do_inference(frame, model)

    # 예측 클래스를 프레임에 표시
    cv2.putText(frame, str(predicted_class), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,0,0), 2)


        # 화면에 프레임 표시
    cv2.imshow('Frame', frame)

    # 'q'를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 작업 완료 후 해제
cap.release()

# 모든 창 닫기
cv2.destroyAllWindows()
