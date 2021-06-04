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
    print("Received message: " + msg.topic + " -> " + msg.payload.decode("utf-8"))

login = "temp_sensor"
password = "Qwerty123"

# Создание клиента
client = mqtt.Client("Publisher")
client.on_connect = on_connect

# Включение TLS
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)

client.username_pw_set(login, password)

# Подключение к HiveMQ Cloud на порт 8883
client.connect("2936de5e78ca44d4ae75866ea24136b6.s1.eu.hivemq.cloud", 8883)

# Подписывается на топик "my/test/topic"
topic_for_post = "my/test/topic"
client.subscribe(topic_for_post)

# Эмуляция температуры и постинг сообщений
# ______________________________________________________________________________________________________________

import numpy as np
import matplotlib.pyplot as plt

graph_wide = 100
average_temp = 35
load_start_value = 35
temp_start_value = 37
plt.axis([0, 10, 0, 1])
load_visible = np.zeros(graph_wide)
temp_visible = np.zeros(graph_wide)
cooler_visible = np.zeros(graph_wide)
x_axis = np.arange(graph_wide)


# Функция для нового значения нагрузки
def new_load_value(value):
    rare_increase = np.random.normal(0, scale = 4.5, size = 1)
    # new_value = np.random.randint(value-3, value+4, size = 1) + rare_increase               #Вариант 1
    new_value = abs(np.random.normal(value, scale = 3, size = 1)) + rare_increase             #Вариант 2
    if new_value < 30:
        return np.random.randint(30, 34, size = 1)
    else:
        return new_value


# Функция для нового значения температуры
def new_temp_value(value):
    average_increase = 0
    cooler_correction = cooler_value * 2
    aver_count=4
    temp_sum = 0
    for i in range(aver_count):
        average_increase += load_visible[graph_wide-i-1] - load_visible[graph_wide-i-2]
        temp_sum += load_visible[graph_wide-i-1]
    if average_increase > 0:
        temp_change = np.random.randint(1, 4, size=1)
    else:
        temp_change = np.random.randint(-2, 1, size=1)

    if average_increase > 0 and float(value+15) < temp_sum/aver_count:
        temp_change = np.random.randint(5, 8, size=1)


    new_value = value + temp_change - cooler_correction
    if new_value < 29 and cooler_correction > 0:
        return np.random.randint(26, 32, size = 1)
    if new_value < 29 and cooler_correction == 0:
        return np.random.randint(31, 36, size = 1)
    else:
        return new_value

fig, graphics = plt.subplots(2)

UDP_IP = "127.0.0.1"
UDP_PORT = 8094

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.1)

while True:

    # Получение данных от кулера
    try:
        data = sock.recv(4)  # Размер буфера
        cooler_value = int(data)
        new_visible = np.delete(cooler_visible, 0)
        cooler_visible = np.append(new_visible, cooler_value)
    except Exception:
        cooler_value = 0

    # Обновление графика загрузки
    last_element_load = new_load_value(load_start_value)
    if last_element_load > 100:
        last_element_load = 100
    load_start_value = last_element_load
    new_visible = np.delete(load_visible, 0)
    load_visible = np.append(new_visible, last_element_load)

    # Обновление графика температуры
    last_element_temp = new_temp_value(temp_start_value)
    temp_start_value = last_element_temp
    new_visible = np.delete(temp_visible, 0)
    temp_visible = np.append(new_visible, last_element_temp)

    # Отрисовка графика

    fig.suptitle('Мониторинг параметров')
    graphics[0].cla()
    graphics[0].plot(x_axis, temp_visible, label='Temperature')
    graphics[0].plot(x_axis, load_visible, label='Load')
    graphics[0].legend(bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
    graphics[0].set_ylim(0, 100)
    graphics[1].cla()
    graphics[1].plot(x_axis, cooler_visible, label='Cooler power', color='r')
    graphics[1].set_ylim(-0.2, 3.2)
    graphics[1].legend(bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
    plt.subplots_adjust(right=0.72)
    plt.pause(0.2)

    plt.close(1)

    client.publish(topic_for_post, int(last_element_temp))
    if last_element_temp >= 100:
        print("System poweroff")
        break

plt.show()

# ______________________________________________________________________________________________________________

# Запуск петли
client.loop_forever()