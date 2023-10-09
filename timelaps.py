import argparse
from picamera import PiCamera
from time import sleep

parser = argparse.ArgumentParser(description='촬영 변수를 설정하세요.')
parser.add_argument('--type', default=1, type=float, help='촬영 타입을 입력하세요.')
parser.add_argument('--width', default=480, type=int, help='가로 픽셀수를 입력하세요')
parser.add_argument('--heigth', default=480, type=int, help='세로 픽셀수를 입력하세요')
args = parser.parse_args() #parse_args() 메서드를 호출하여 명령줄 인수를 파싱하고 변수에 저장

camera = PiCamera() # PiCamera 객체 생성 및 camera 변수에 할당
camera.resolution = (args.width, args.height)

file_name_pattern = args.path # 파일 이름 패턴 설정

if args.type == 'image':
    parser = argparse.ArgumentParser(description='촬영 변수를 설정하세요.')
    parser.add_argument('--path', default=480, type=int, help='파일의 경로와 이름, 형식자를 입력하세요')
    args = parser.parse_args() #parse_args() 메서드를 호출하여 명령줄 인수를 파싱하고 변수에 저장

    camera.start_preview()
    # sleep(5) : 촬영 전에 대기시간을 얼마나 줄지 결정하는 코드인데 필요 없으면 지우면 됨.
    camera.capture(args.path) #사진 찍고 경로와 저장 파일 이름 설정
    #사진이 돌아가면 각도 조절하는 코드 : camera.rotation = 180
    camera.stop_preview() #미리보기 끄기
    camera.close() # 카메라 객체 닫기

elif args.type == 'video':
    parser = argparse.ArgumentParser(description='촬영 변수를 설정하세요.')
    parser.add_argument('--time', default=1, type=float, help='촬영 시간을 입력하세요.')
    parser.add_argument('--frame', default=15, type=int, help='FPS를 입력하세요')
    parser.add_argument('--path', default=480, type=int, help='파일의 경로와 이름, 형식자를 입력하세요')
    args = parser.parse_args() #parse_args() 메서드를 호출하여 명령줄 인수를 파싱하고 변수에 저장

    camera.framerate = args.frame #초당 프레임 설정
    camera.start_preview()
    #sleep(2) : 촬영 전에 대기시간을 얼마나 줄지 결정하는 코드인데 필요 없으면 지우면 됨.
    camera.start_recording(args.path) #촬영한 동영상을 입력받은 path에 저장
    sleep(args.time) #10초간 촬영한다는 뜻
    camera.stop_recording()
    camera.stop_preview()

else:
    print("image 또는 video를 입력하세요.")