"""Observe PyPubSub routing and message validation in an isolated publisher."""

from pubsub.core import Publisher
from pubsub.core.topicargspec import (
    SenderMissingReqdMsgDataError,
    SenderUnknownMsgDataError,
)
from python_protocol import fields

from .helpers import integer, mapping


class Consumer:
    """Keep fixed topic specifications and a retained listener per trace."""

    def __init__(self):
        self.publisher = Publisher()
        self.log = []
        for topic in ("document", "document.changed"):
            self.publisher.getTopicMgr().getOrCreateTopic(
                topic, protoListener=self.receive
            )

    def receive(self, value):
        """Record actual deliveries without assuming listener ordering."""
        self.log.append(value)

    def step(self, event):
        op = event.get("op")
        fields(event, ("op", "topic", "data") if op == "send" else ("op", "topic"))
        topic = event["topic"]
        if topic not in ("document", "document.changed"):
            raise ValueError("unsupported topic")
        error = None
        if op == "subscribe":
            self.publisher.subscribe(self.receive, topic)
        elif op == "unsubscribe":
            self.publisher.unsubscribe(self.receive, topic)
        elif op == "send":
            data = mapping(event["data"])
            for value in data.values():
                integer(value)
            try:
                self.publisher.sendMessage(topic, **data)
            except (SenderMissingReqdMsgDataError, SenderUnknownMsgDataError) as exc:
                error = type(exc).__name__
        else:
            raise ValueError("unsupported event")
        return {"log": list(self.log), "error": error}
