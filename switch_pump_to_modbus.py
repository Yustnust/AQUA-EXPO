import serial
import time

# ===== 请改成你的实际串口号 =====
PORT = 'COM3'

# 查询当前协议
QUERY  = bytes.fromhex('91 EB 07 00 00 00 00 00 00 D5 28 FF F8')
# 切换到 Modbus 协议
SWITCH = bytes.fromhex('91 EB 03 00 00 06 08 00 00 67 0D 51 BB')

def send_and_read(ser, data, desc):
    print(f'\n[{desc}] 发送: {data.hex(" ").upper()}')
    ser.write(data)
    time.sleep(0.3)
    rx = ser.read(ser.in_waiting or 13)
    if rx:
        print(f'[{desc}] 收到: {rx.hex(" ").upper()}')
    else:
        print(f'[{desc}] 未收到回码，请检查接线和串口号')

with serial.Serial(PORT, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1) as ser:
    print(f'已打开 {PORT}, 9600/8/N/1')
    send_and_read(ser, QUERY, '查询当前协议')
    input('\n确认要切换到 Modbus 吗？切换后必须断电重启。按回车继续...')
    send_and_read(ser, SWITCH, '切换为 Modbus')
    print('\n现在请给泵断电，再重新上电，之后可用 Modbus RTU 9600/8/N/1 读取 41001 验证。')