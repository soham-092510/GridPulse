import json
import logging
import asyncio
from typing import Optional, Callable
import paho.mqtt.client as mqtt
from app.core.config import settings
from app.ingestion.normalizer import MeasurementNormalizer
from app.ingestion.validator import validator_engine

logger = logging.getLogger("neighbourflex.mqtt")

class MQTTIngestionBridge:
    """Subscribes to IoT MQTT telemetry and forwards validated packets to the engine."""
    
    def __init__(self, on_message_callback: Optional[Callable] = None):
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self.on_message_callback = on_message_callback
        
    def start(self):
        """Attempts connection to MQTT broker."""
        try:
            self.client = mqtt.Client(client_id="neighbourflex_backend", protocol=mqtt.MQTTv5)
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect
            
            # Connect in non-blocking background thread
            self.client.connect_async(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
            self.client.loop_start()
            logger.info(f"MQTT client started for {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
        except Exception as e:
            logger.warning(f"Could not connect to MQTT Broker ({e}). System will use REST/WebSocket ingestion.")
            self.is_connected = False

    def stop(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.is_connected = True
            logger.info("Connected to MQTT broker successfully.")
            # Subscribe to all telemetry subtopics
            client.subscribe(f"{settings.MQTT_TOPIC_PREFIX}/#")
        else:
            logger.warning(f"Failed to connect to MQTT broker with code {rc}")
            self.is_connected = False

    def _on_disconnect(self, client, userdata, rc, properties=None):
        self.is_connected = False
        logger.info("Disconnected from MQTT broker.")

    def _on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload_str = msg.payload.decode("utf-8")
            data = json.loads(payload_str)
            
            # Example payload: {"device_id": "METER_01", "metric": "power", "value": 45.2, "unit": "kW"}
            device_id = data.get("device_id", "UNKNOWN_DEV")
            raw_metric = data.get("metric", "active_power")
            raw_val = float(data.get("value", 0.0))
            raw_unit = data.get("unit", "kW")
            
            metric, norm_val, unit = MeasurementNormalizer.normalize(raw_metric, raw_val, raw_unit)
            quality, conf, reason = validator_engine.validate(device_id, metric, norm_val)
            
            packet = {
                "device_id": device_id,
                "metric": metric,
                "value": norm_val,
                "unit": unit,
                "quality": quality,
                "confidence": conf,
                "warning": reason,
                "topic": topic
            }
            
            if self.on_message_callback:
                self.on_message_callback(packet)
        except Exception as e:
            logger.error(f"Error parsing MQTT message on {msg.topic}: {e}")

mqtt_bridge = MQTTIngestionBridge()
