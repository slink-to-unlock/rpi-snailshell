from picamera import PiCamera
from time import sleep

camera = PiCamera() #PiCamera 객체 생성 및 camera 변수에 할당

camera.start_preview() #카메라 프리뷰 시작

for i in range(횟수): #횟수만큼 캡쳐 반복
   sleep(시간) #촬영 간격 설정, 카메라 조도 설정을 위해 최소 2초 이상 설정
   camera.capture('/home/pi/image%s.jpg' % i) #파일 경로 및 이름 생성하고 캡쳐

camera.stop_preview() #프리뷰 끝내기