# 서드파티
import cv2

# 프로젝트
from snailshell.model_loader.resnet import ResNetAdapter
from snailshell.model_loader.mobilenet import MobileNetAdapter


class BasePipeline:

    def __init__(
        self,
        backend,
        model_name: str,
        weight_path: str,
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

        self.frame_loader = backend
        self.model = model
        self.use_arduino = use_arduino
        self.visualize = visualize
        self.target_fps = target_fps
        if self.use_arduino:
            import serial
            self.serial = serial.Serial('/dev/ttyACM0', 9600)

    def run(self):
        self.frame_loader.initialize()
        frame_interval = int(self.frame_loader.fps / self.target_fps)
        frame_count = 0
        while True:
            frame = self.frame_loader.get_frame()
            if frame is None:
                print('리턴받은 프레임이 없습니다.')
                break

            frame_count += 1
            if frame_count == frame_interval:
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

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.frame_loader.release()
        cv2.destroyAllWindows()
