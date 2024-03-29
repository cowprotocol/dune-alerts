"""
Since channel is fixed at the beginning and nobody wants to see unfurled media
(especially in an alert), this tiny class encapsulates a few things that would
otherwise be unnecessarily repeated.
"""
import ssl
import logging.config
import certifi

from slack.errors import SlackApiError
from slack.web.client import WebClient

from src.post.base import PostClient

log = logging.getLogger(__name__)
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)


class BasicSlackClient(PostClient):
    """
    Basic Slack Client with message post functionality
    constructed from an API token and channel
    """

    def __init__(self, token: str, channel: str) -> None:
        self.client = WebClient(
            token=token,
            # https://stackoverflow.com/questions/59808346/python-3-slack-client-ssl-sslcertverificationerror
            ssl=ssl.create_default_context(cafile=certifi.where()),
        )
        self.channel = channel

    def post(self, message: str) -> None:
        """Posts `message` to `self.channel` excluding link previews."""
        log.info(f"posting to slack channel: {self.channel}")
        try:
            self.client.chat_postMessage(
                channel=self.channel,
                text=message,
                # Do not show link preview!
                # https://api.slack.com/reference/messaging/link-unfurling
                unfurl_media=False,
            )
        except SlackApiError as err:
            raise RuntimeError(f"slack post failed with {err}") from err
