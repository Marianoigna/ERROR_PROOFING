<div align="center">

# 🛡️ ERROR PROOFING — AIS BOX

### Monitor de temperatura IoT en tiempo real

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django Channels](https://img.shields.io/badge/Channels-WebSockets-FF4444?style=for-the-badge&logo=django&logoColor=white)](https://channels.readthedocs.io/)
[![MQTT](https://img.shields.io/badge/MQTT-paho--mqtt-660066?style=for-the-badge&logo=eclipse-mosquitto&logoColor=white)](https://mqtt.org/)
[![DRF](https://img.shields.io/badge/DRF-REST%20Framework-A30000?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)

</div>

---

## 📖 ¿Qué es esto?

**AIS BOX — Error Proofing** es un sistema de monitoreo de temperatura IoT en tiempo real. Captura lecturas de sensores físicos via **MQTT**, las persiste en una base de datos y las transmite instantáneamente a un **dashboard web** usando **WebSockets**.

> Sin polling. Sin recargas. Los datos llegan solos. ⚡

---

## 🏗️ Arquitectura

```
┌─────────────┐     MQTT      ┌──────────────────┐     HTTP POST     ┌─────────────────┐
│   Sensor    │ ─────────────▶│ mqtt_subscriber  │ ────────────────▶ │   Django REST   │
│  Físico 🌡️  │  topic:       │      .py         │  /api/temperatura/│      API        │
└─────────────┘  sensores/    └──────────────────┘                   └────────┬────────┘
                 temperatura                                                   │
                                                                        guarda │ SQLite3
                                                                               │
                                                                      ┌────────▼────────┐
                                                                      │  Channel Layer  │
                                                                      │  (InMemory/     │
                                                                      │   Redis)        │
                                                                      └────────┬────────┘
                                                                               │ WebSocket
                                                                      ┌────────▼────────┐
                                                                      │   Dashboard     │
                                                                      │   Browser 🖥️    │
                                                                      └─────────────────┘
```

---

## ✨ Features

| Feature | Descripción |
|---------|-------------|
| 📡 **Ingesta MQTT** | Recibe datos del broker MQTT (Mosquitto, HiveMQ, etc.) |
| 🔌 **WebSockets** | Push en tiempo real a todos los clientes conectados |
| 🌡️ **Color dinámico** | Rojo si `≥ 40°C`, azul si `≤ 10°C`, normal en rango |
| 📊 **Historial** | Últimas 20 lecturas visibles en el dashboard |
| 🔄 **Auto-reconexión** | El WebSocket se reconecta automáticamente si cae |
| 🗃️ **REST API** | Endpoint para consultar o inyectar lecturas manualmente |
| 🐍 **ASGI** | Servidor Daphne para manejar HTTP y WebSockets en simultáneo |

---

## 🚀 Inicio rápido

### 1. Clonar e instalar dependencias

```bash
git clone https://github.com/Marianoigna/ERROR_PROOFING.git
cd ERROR_PROOFING

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install django djangorestframework channels daphne paho-mqtt requests
```

### 2. Configurar la base de datos

```bash
python manage.py migrate
```

### 3. Levantar el servidor

```bash
python manage.py runserver
```

> El servidor Daphne (ASGI) arranca automáticamente gracias a la configuración de `ASGI_APPLICATION`.

### 4. Iniciar el suscriptor MQTT *(opcional — si tenés un broker)*

Edita las variables de configuración en `mqtt_subscriber.py`:

```python
MQTT_BROKER   = 'localhost'          # IP o hostname del broker
MQTT_PORT     = 1883
MQTT_TOPIC    = 'sensores/temperatura'
MQTT_USER     = ''                   # Si tu broker requiere auth
MQTT_PASSWORD = ''
SENSOR_ID     = 'sensor_01'
```

Luego correlo en otra terminal:

```bash
python mqtt_subscriber.py
```

### 5. Abrir el dashboard

```
http://127.0.0.1:8000/
```

---

## 📡 API Reference

### `GET /api/temperatura/`

Retorna las últimas 50 lecturas almacenadas.

```json
[
  {
    "id": 42,
    "sensor_id": "sensor_01",
    "valor": 25.3,
    "timestamp": "2025-04-13T01:00:00.000Z"
  }
]
```

### `POST /api/temperatura/`

Registra una nueva lectura y notifica a todos los clientes WebSocket.

**Body:**
```json
{
  "sensor_id": "sensor_01",
  "valor": 23.5
}
```

**Response `201 Created`:**
```json
{
  "id": 43,
  "sensor_id": "sensor_01",
  "valor": 23.5,
  "timestamp": "2025-04-13T01:00:05.123Z"
}
```

---

## 🔌 WebSocket

Conectate al canal de temperatura en tiempo real:

```
ws://localhost:8000/ws/temperatura/
```

**Mensaje recibido (JSON):**
```json
{
  "sensor_id": "sensor_01",
  "valor": 27.8,
  "timestamp": "2025-04-13T01:00:10.456Z"
}
```

Ejemplo en JavaScript:
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/temperatura/');

socket.onmessage = (event) => {
  const { sensor_id, valor, timestamp } = JSON.parse(event.data);
  console.log(`${sensor_id}: ${valor}°C @ ${timestamp}`);
};
```

---

## 📁 Estructura del proyecto

```
ERROR_PROOFING/
├── ERROR_PROOFING/          # Configuración principal de Django
│   ├── settings.py          # Ajustes del proyecto (DB, Channels, DRF)
│   ├── urls.py              # Rutas HTTP raíz
│   ├── asgi.py              # Punto de entrada ASGI (HTTP + WS)
│   └── wsgi.py              # Punto de entrada WSGI (legacy)
│
├── AIS_BOX/                 # App principal
│   ├── models.py            # Modelo Temperatura
│   ├── serializers.py       # Serializer DRF
│   ├── views.py             # API REST (GET/POST temperatura)
│   ├── consumers.py         # Consumer WebSocket
│   ├── routing.py           # Rutas WebSocket
│   ├── urls.py              # Rutas HTTP de la app
│   └── templates/
│       └── AIS_BOX/
│           └── dashboard.html   # Dashboard en tiempo real
│
├── mqtt_subscriber.py       # Cliente MQTT → llama a la REST API
└── manage.py
```

---

## ⚙️ Configuración avanzada

### Usar Redis para producción

El Channel Layer en memoria no escala a múltiples procesos. Para producción, cambiá a Redis:

```bash
pip install channels-redis
```

```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    }
}
```

### Payload MQTT aceptado

El suscriptor acepta dos formatos:

```
# Valor numérico simple
23.5

# JSON con metadatos
{"valor": 23.5, "sensor_id": "sensor_02"}
```

---

## 🛠️ Stack tecnológico

| Tecnología | Rol |
|------------|-----|
| **Django 6** | Framework web + ORM + Admin |
| **Django REST Framework** | API REST |
| **Django Channels + Daphne** | WebSockets (ASGI) |
| **paho-mqtt** | Cliente MQTT |
| **SQLite3** | Base de datos (dev) |
| **InMemoryChannelLayer** | Channel Layer (dev) |

---

## 📄 Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).

---

<div align="center">

Hecho con ❤️ por [Marianoigna](https://github.com/Marianoigna)

</div>
