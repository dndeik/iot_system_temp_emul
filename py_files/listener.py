import paho.mqtt.client as mqtt
import socket

# Функция для проверки соединения
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print("Connect returned result code: " + str(rc))

# Функция получения сообщения
def on_message(client, userdata, msg):
    global received_value
    received_value = int(msg.payload.decode("utf-8"))


received_value = 0
login = "temp_sensor"
password = "Qwerty123"

# Создание клиента
client = mqtt.Client("Listener")
client.on_connect = on_connect


# Включение TLS
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)


client.username_pw_set(login, password)

# Подключение к HiveMQ Cloud на порт 8883
client.connect("2936de5e78ca44d4ae75866ea24136b6.s1.eu.hivemq.cloud", 8883)

# Подписывается на топик "my/test/topic"
client.subscribe("my/test/topic")

# Получение сообщений и реакция
cooler_power = 0
udp_ip = "127.0.0.1"
udp_port = 8094

# Для интерфейса
# ____________________________________________________________________________________________________________
from tkinter import *
from PIL import ImageTk, Image

size = 600
root = Tk()
canvas = Canvas(root, width=size, height=size)
canvas.pack()
x0 = 75
y0 = 450
d = 50

img = Image.open("cool_cooler.png")
width = 410
cooler_img = img.resize((width, width), Image.ANTIALIAS)
# ____________________________________________________________________________________________________________

while True:
    client.loop_start()
    client.on_message = on_message
    client.loop_stop()

    if received_value > 45 and received_value < 60:
        cooler_power = 1
    elif received_value >= 60 and received_value < 80:
        cooler_power = 2
    elif received_value >= 80:
        cooler_power = 3
    else:
        cooler_power = 0

    udp_message = b"%d" % cooler_power

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(udp_message, (udp_ip, udp_port))

    # Отрисовка интерфейса
    x0 = 75
    y0 = 480
    d = 50
    image = ImageTk.PhotoImage(cooler_img)
    imagesprite = canvas.create_image(300, 240, image=image)

    for i in range(3):
        x0 += 100
        if i == cooler_power-1:
            canvas.create_oval(x0, y0, x0 + d, y0 + d, fill='#65EC3B')
        else:
            canvas.create_oval(x0, y0, x0 + d, y0 + d, fill='grey')

    root.update()