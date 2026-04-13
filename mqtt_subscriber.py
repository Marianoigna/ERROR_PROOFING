"""
mqtt_subscriber.py
==================
Escucha un broker MQTT y reenvía cada lectura de temperatura
a la API REST de Django, que la guarda en SQLite3 y notifica
via WebSocket a todos los clientes conectados.

Uso:
    python mqtt_subscriber.py

Configuración:
    Edita las variables de la sección CONFIG según tu entorno.
"""

import json
import requests
import paho.mqtt.client as mqtt

# ── CONFIG ────────────────────────────────────────────────────────────────────
MQTT_BROKER   = 'localhost'       # IP o hostname del broker MQTT (ej. Mosquitto)
MQTT_PORT     = 1883
MQTT_TOPIC    = 'sensores/temperatura'
MQTT_USER     = ''                # dejar vacío si no hay autenticación
MQTT_PASSWORD = ''

API_URL       = 'http://127.0.0.1:8000/api/temperatura/'
SENSOR_ID     = 'sensor_01'
# ─────────────────────────────────────────────────────────────────────────────


def on_connect(client, userdata, flags, reason_code, properties):
    print(f'[MQTT] Conectado al broker {MQTT_BROKER}:{MQTT_PORT}')
    client.subscribe(MQTT_TOPIC)
    print(f'[MQTT] Suscrito al topic: {MQTT_TOPIC}')


def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8').strip()
    print(f'[MQTT] Mensaje recibido: {payload}')

    try:
        # El sensor puede enviar solo el número ("23.5")
        # o un JSON ({"valor": 23.5, "sensor_id": "sensor_01"})
        try:
            data = json.loads(payload)
            valor     = float(data.get('valor', data))
            sensor_id = data.get('sensor_id', SENSOR_ID)
        except (json.JSONDecodeError, TypeError):
            valor     = float(payload)
            sensor_id = SENSOR_ID

        # Enviar a la API REST de Django
        response = requests.post(API_URL, json={
            'valor':     valor,
            'sensor_id': sensor_id,
        }, timeout=5)

        if response.status_code == 201:
            print(f'[API]  ✔ Guardado: {sensor_id} → {valor}°C')
        else:
            print(f'[API]  ✘ Error {response.status_code}: {response.text}')

    except ValueError as e:
        print(f'[ERROR] No se pudo parsear el valor: {payload} — {e}')
    except requests.RequestException as e:
        print(f'[ERROR] No se pudo conectar a la API: {e}')


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    print(f'[MQTT] Conectando a {MQTT_BROKER}:{MQTT_PORT} ...')
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_forever()


if __name__ == '__main__':
    main()
