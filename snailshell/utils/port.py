# 내장
from typing import Union

# 서드파티
import serial.tools.list_ports


def get_arduino_serial_ports(port: Union[str, None] = None):
    found_ports = list(serial.tools.list_ports.comports())
    for found_port in found_ports:
        # 아두이노 장치를 찾음 (일부 아두이노는 'Arduino'라는 단어를 포트 설명에 포함함)
        if 'Arduino' in found_port.description:
            print(f'아두이노 `{found_port.device}` 를 찾았습니다.')
            if port:
                # 포트를 명시적으로 지정한 경우
                if port == found_port.device:
                    return port
                else:
                    print(f'주어진 포트 `{port}` 와 다릅니다.')
            else:
                return found_port.device
    print('아두이노를 찾지 못했습니다.')
    return None


if __name__ == '__main__':
    get_arduino_serial_ports()
