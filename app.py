import paho.mqtt.client as mqtt
import serial
import time
import json 

with open(".config.json") as config_file:
    config = json.load(config_file)

mqtt_config = config["mqtt"]
serial_config = config["serial"]

mqtt_broker = mqtt_config["broker"]
mqtt_port = mqtt_config["port"]
mqtt_username = mqtt_config["username"]
mqtt_password = mqtt_config["password"]
mqtt_command_topic = mqtt_config["command_topic"]
mqtt_report = mqtt_config["report_topic"]
mqtt_state = mqtt_config["state_topic"]

serial_port = serial_config["port"]
baud_rate = serial_config["baud_rate"]

ser = serial.Serial(serial_port, baud_rate, timeout=1)

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with code:", rc)
    client.subscribe(mqtt_command_topic)

def on_message(client, userdata, msg):
    command_payload = msg.payload.decode()

    serial_command = f"\x08{command_payload}\r\n"
    ser.write(serial_command.encode())

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(mqtt_username, mqtt_password)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, mqtt_port, keepalive=60)

def serial_read_publish():
    while True:
        data = ser.readline().decode().strip()
        cleaned_data = data.replace(">", "")
        if data:
            mqtt_client.publish(mqtt_report, cleaned_data)

mqtt_client.loop_start()

serial_read_publish()
