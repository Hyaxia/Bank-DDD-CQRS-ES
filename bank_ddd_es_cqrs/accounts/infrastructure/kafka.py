from typing import Callable, Type
import json
from threading import Thread
from kafka import KafkaConsumer
from ...shared.model import BaseEvent
from ..model import events as account_module_events


class KafkaEventConsumer:
    def __init__(self, bootstrap_servers: str, topic: str, consumer_group_id: str):
        self.consumer = KafkaConsumer(topic, bootstrap_servers=bootstrap_servers, group_id=consumer_group_id)

    def _event_model_to_core(self, event_msg) -> BaseEvent:
        class_name = event_msg['name']
        kwargs = json.loads(event_msg['data'])
        event_class: Type[BaseEvent] = getattr(account_module_events, class_name)
        return event_class(**kwargs)

    def read(self, trigger: Callable[[BaseEvent], None]):
        for kafka_msg in self.consumer:
            event_data = json.loads(kafka_msg.value)['payload']['after']
            core_event = self._event_model_to_core(event_data)
            trigger(core_event)


def start_kafka_consumer(trigger: Callable[[BaseEvent], None], bootstrap_servers: str, topic: str,
                         consumer_group_id: str):
    event_consumer = KafkaEventConsumer(bootstrap_servers, topic, consumer_group_id)
    thread = Thread(target=event_consumer.read, args=(trigger,))
    thread.start()
