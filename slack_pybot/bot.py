
from typing import Callable, Dict, List
from redis import StrictRedis
import time
from slackclient import SlackClient
from .data import Bot, Command, Event


class PyBot(SlackClient):

    def __init__(self, token: str, bot: Bot, db: StrictRedis) -> None:
        super().__init__(token)
        if (not self.rtm_connect()):
            raise IOError('Connection to Slack failed, check your token')
        self.bot = bot
        self.db = db
        self._triggers: Dict = {}
        self._USER_CACHE: Dict[str, object] = {}

    def _getCachedUser(self, user_id: int):
        # store a cache of userId -> userName mappings,
        # so we don't need to make API calls every time
        if not self._USER_CACHE.get(user_id):
            self._USER_CACHE[user_id] = self.api_call(
                'users.info', user=user_id
            )['user']
        return self._USER_CACHE[user_id]

    def postMessage(self, channel: str, message: str, thread: str):
        self.api_call(
            'chat.postMessage',
            channel=channel,
            text=message,
            thread_ts=thread,
            username=self.bot.name,
            icon_emoji=self.bot.icon_emoji
        )

    def register(self, trigger: str, callback, condition):
        # registers a trigger, which fires a callback if condition is true
        maybeCallback = _MaybeCallback(callback, condition)
        self._triggers.setdefault(trigger, [maybeCallback])

    def notify(self, command: Command):
        # notifies all subscribers when command triggers, if condition is true
        for mc in (self._triggers.get(command.trigger, [])):
            if mc.condition(command.event):
                mc.callback(command)

    def listen(self):
        # listens for commands, and process them in turn
        while True:
            events = filter(lambda e: e.get('type') ==
                            'message' and 'text' in e, self.rtm_read())
            for event in events:
                command = self._messageEventToCommand(event)
                if command:
                    self.notify(command)  # notifies all listeners
            time.sleep(0.5)

    def _messageEventToCommand(self, event: Event):
        for trigger in self._triggers.keys():
            if event['text'].startswith(trigger):
                args = event['text'][len(trigger):].strip().split()
                return Command(
                    trigger,
                    args,
                    Event(
                        event.get('type'),
                        event.get('subtype'),
                        event.get('channel'),
                        event.get('user'),
                        event.get('text'),
                        event.get('ts'),
                        event.get('thread_ts')
                    ),
                    self._getCachedUser(event.user_id)
                )

        return None


def threaded(event):
    return allMessageEvents(event) and event.thread is not None


def messageEvents(event):
    return allMessageEvents(event) and event.thread is None


def allMessageEvents(event):
    return (
        event.type == 'message' and
        event.subtype is None and
        event.text is not None
    )


class _MaybeCallback(object):
    def __init__(self, callback, condition):
        self.callback = callback
        self.condition = condition
