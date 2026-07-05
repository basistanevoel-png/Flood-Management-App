from paho.mqtt import client as mqtt
from queue import Queue
import ssl, json, os

from dotenv import load_dotenv
load_dotenv()

#DEPRECATED, WILL UPDATE SOON TO MIMIC BLYNK LISTENER RETURN RESPONSE
def start_mqtt_listener(msg_queue : Queue):

    BROKER = os.getenv("BROKER_URL")
    PORT = int(os.getenv("BROKER_PORT"))
    USERNAME = os.getenv("BROKER_USERNAME")
    PASSWORD = os.getenv("BROKER_PASSWORD")
    TOPIC = os.getenv("TOPIC")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
            client.subscribe(TOPIC)
        else:
            print("Failed to connect: ", rc)

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
        except json.JSONDecodeError:
            payload = msg.payload.decode()

        msg_queue.put(payload)
        print(f"[MQTT] {msg.topic}: {payload}")

        print(f"[QUEUE] Size: {msg_queue.qsize()}")

    client = mqtt.Client(client_id="django_mqtt_listener", protocol=mqtt.MQTTv311)
    client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
    client.username_pw_set(USERNAME, PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)

    print("MQTT listener running...")

    client.loop_forever()