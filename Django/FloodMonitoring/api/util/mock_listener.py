import ssl, time, os
from paho.mqtt import client as mqtt

from dotenv import load_dotenv
load_dotenv()

class MQTTTestListener:
    def __init__(self, broker_url, broker_port, username, password, topic):
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.topic = topic

        self.client = mqtt.Client(protocol=mqtt.MQTTv311)
        self.client.username_pw_set(self.username, self.password)
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[LISTENER] Connected to broker")
            client.subscribe(self.topic)
            print(f"[LISTENER] Subscribed to topic: {self.topic}")
        else:
            print(f"[LISTENER] Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            print(f"\n[LISTENER] Message received on topic '{msg.topic}':")
            print(payload)
        except Exception as e:
            print(f"[LISTENER] Error decoding message: {e}")

    def start(self):
        try:
            print(f"[LISTENER] Connecting to {self.broker_url}:{self.broker_port}...")
            self.client.connect(self.broker_url, self.broker_port)
        except Exception as e:
            print(f"[LISTENER] Connection error: {e}")
            return

        self.client.loop_forever()


def start_listener():
    BROKER_URL = os.getenv("BROKER_URL")
    BROKER_PORT = int(os.getenv("BROKER_PORT"))
    BROKER_USERNAME = os.getenv("BROKER_USERNAME")
    BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")
    TOPIC = os.getenv("TOPIC")

    listener = MQTTTestListener(
        broker_url=BROKER_URL,
        broker_port=BROKER_PORT,
        username=BROKER_USERNAME,
        password=BROKER_PASSWORD,
        topic=TOPIC
    )

    listener.start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    start_listener()