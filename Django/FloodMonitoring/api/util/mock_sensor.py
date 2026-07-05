import ssl, os, json, random, time, threading
from paho.mqtt import client as mqtt

from dotenv import load_dotenv
load_dotenv()

class MockMicrocontroller:
    def __init__(self, mcu_id, sensor_ids_connected, broker_url, broker_port, broker_uname, broker_pword, topic, publish_interval=300):
        self.mcu_id = mcu_id
        self.sensor_ids_connected = sensor_ids_connected
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.broker_uname = broker_uname
        self.broker_pword = broker_pword
        self.topic = topic
        self.publish_interval = publish_interval
        self.connected = False

        self.client = mqtt.Client(client_id=self.mcu_id, protocol=mqtt.MQTTv311)
        self.client.username_pw_set(self.broker_uname, self.broker_pword)
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.on_connect = self.on_connect

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[{self.mcu_id}] Connected to broker")
            self.connected = True
        else:
            print(f"[{self.mcu_id}] Failed to connect, code {rc}")

    def start(self):
        try:
            print(f"[{self.mcu_id}] Attempting to connect to {self.broker_url}:{self.broker_port}...")
            self.client.connect(self.broker_url, self.broker_port)
        except Exception as e:
            print(f"[{self.mcu_id}] Connection exception: {e}")
            return

        self.client.loop_start()

        threading.Thread(target=self.publish_loop, daemon=True).start()

    def publish_loop(self):
        while not self.connected:
            time.sleep(0.1)

        while True:
            sensor_readings = []

            for sensor_id in self.sensor_ids_connected:
                sensor_readings.append({
                    "sensor_id": sensor_id,
                    "distance": round(random.uniform(0, 2000), 2),
                })

            payload = json.dumps({
                "mcu_id": self.mcu_id,
                "readings": sensor_readings,
            })

            print(f"[{self.mcu_id}] Publishing → {payload}")
            result = self.client.publish(self.topic, payload)

            print(f"[{self.mcu_id}] Publish result: {result.rc}")
            time.sleep(self.publish_interval)


def start_sensors():
    BROKER_URL = os.getenv("BROKER_URL")
    BROKER_PORT = int(os.getenv("BROKER_PORT"))
    BROKER_USERNAME = os.getenv("BROKER_USERNAME")
    BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")
    TOPIC = os.getenv("TOPIC")

    print("Starting mock sensors...")
    mcu_ids = ['MCU_001', 'MCU_002']
    sensor_id_collections = [["SENS_001", "SENS_002"], ["SENS_003"]]
    
    microcontrollers = []

    count = 0

    for id in mcu_ids:
        microcontroller = MockMicrocontroller(
            mcu_id=id,
            sensor_ids_connected=sensor_id_collections[count],
            broker_url=BROKER_URL,
            broker_port=BROKER_PORT,
            broker_uname=BROKER_USERNAME,
            broker_pword=BROKER_PASSWORD,
            topic=TOPIC,
            publish_interval=300
        )
        microcontroller.start()
        microcontrollers.append(microcontroller)
        print(f"[{id}] Microcontroller instances started")
        count += 1

    while True:
        time.sleep(1)

if __name__ == "__main__":
    start_sensors()
