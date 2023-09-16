import argparse
from picamera import PiCamera
from time import sleep

parser = argparse.ArgumentParser(description='촬영 변수를 설정하세요.')
parser.add_argument('--time', default=1, type=float, help='촬영 시간을 입력하세요.')
parser.add_argument('--frame', default=15, type=int, help='FPS를 입력하세요')
parser.add_argument('--width', default=480, type=int, help='FPS를 입력하세요')
parser.add_argument('--heigth', default=480, type=int, help='FPS를 입력하세요')

args = parser.parse_args() #parse_args() 메서드를 호출하여 명령줄 인수를 파싱하고 변수에 저장

camera = PiCamera() # PiCamera 객체 생성 및 camera 변수에 할당
camera.resolution = (args.width, args.height)
camera.framerate = args.frame

file_name_pattern = '/home/pi/image_%04d.jpg' # 파일 이름 패턴 설정

camera.start_preview() # 카메라 프리뷰 시작

sleep(2) # 2초 대기
camera.capture_sequence([file_name_pattern % i for i in range(args.time * args.frame)]) # 촬영 시작

camera.stop_preview() # 프리뷰 끝내기