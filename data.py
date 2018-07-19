from dataclasses import dataclass
from typing import List


@dataclass
class Bot:
    name: str
    icon_emoji: str


@dataclass
class Event:
    type: str
    subtype: str
    channel: str
    user_id: str
    text: str
    ts: str
    thread: str


@dataclass
class Command:
    trigger: str
    args: List[str]
    event: Event
    user: object

    @property
    def user_name(self) -> str:
        return self.user['name']

    @property
    def channel(self) -> str:
        return self.event.channel

    @property
    def thread(self) -> str:
        return self.event.thread

    def __repr__(self):
        print(
            "{trigger} {args} {event}".format(
                trigger=self.trigger,
                args=self.args,
                event=self.event,
                user=self.user
            )
        )
