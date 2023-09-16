import argparse
from picamera import PiCamera
from time import sleep

parser = argparse.ArgumentParser(description='촬영 횟수와 촬영 간격을 입력하세요.')
parser.add_argument('--camera', type=float, help='촬영 횟수를 입력하세요')
parser.add_argument('--delay', type=float, help='촬영 간격을 입력하세요')

camera = PiCamera() # PiCamera 객체 생성 및 camera 변수에 할당
camera.resolution = (1000, 1000)
camera.framerate = 15

args = parser.parse_args() #parse_args() 메서드를 호출하여 명령줄 인수를 파싱하고 변수에 저장

if args.camera is not None:
    camera = args.camera
else:
    camera = 1  # 기본값을 설정하세요

if args.delay is not None:
    delay = args.delay
else:
    delay = 1  # 기본값을 설정하세요

camera.start_preview() # 카메라 프리뷰 시작

for i in range(camera): # 횟수만큼 캡쳐 반복
   sleep(delay) # 촬영 간격 설정, 카메라 조도 설정을 위해 최소 2초 이상 설정
   camera.capture('/home/pi/image%s.jpg' % i) # 파일 경로 및 이름 생성하고 캡쳐

camera.stop_preview() # 프리뷰 끝내기