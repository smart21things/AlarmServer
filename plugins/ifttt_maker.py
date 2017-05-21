"""IFTTT Maker plugin"""
import urllib.request
import urllib.parse
import urllib.error
from tornado.httpclient import AsyncHTTPClient
from tornado import gen

from core import logger
from core.events import Events

class ifttt_maker(object):
    """Ifttt maker plugin class"""
    def __init__(self, config):
        """Init function for IFTTT plugin"""
        self.config = config
        ifttt_maker_config_session_name = 'ifttt_maker'

        config.IFTTT_MAKER_ENABLE = config.get_val(
            ifttt_maker_config_session_name, 'enable', False, 'bool')
        if config.IFTTT_MAKER_ENABLE:
            config.IFTTT_MAKER_KEY = config.get_val(
                ifttt_maker_config_session_name, 'key', False, 'str')
            config.IFTTT_MAKER_EVENT_NAME = config.get_val(
                ifttt_maker_config_session_name, 'eventName', False, 'str')
            if config.IFTTT_MAKER_KEY != False:
                config.IFTTT_MAKER_IGNOREZONES = config.get_val(
                    ifttt_maker_config_session_name, 'ignorezones', [], 'listint')
                config.IFTTT_MAKER_IGNOREPARTITIONS = config.get_val(
                    ifttt_maker_config_session_name, 'ignorepartitions', [], 'listint')
                logger.debug('IFTTT_MAKER Enabled - Partitions Ignored: %s - Zones Ignored: %s' %
                             (",".join([str(i) for i in config.IFTTT_MAKER_IGNOREPARTITIONS]),
                              ",".join([str(i) for i in config.IFTTT_MAKER_IGNOREZONES])))
                Events.register('statechange', self.send_notification,
                                config.IFTTT_MAKER_IGNOREPARTITIONS, config.IFTTT_MAKER_IGNOREZONES)

    def send_notification(self, event_type, type, parameters, code, event, message, default_status): #pylint: disable=W0613
        """Send IFTTT notification"""
        self.ifttt_maker_request('notify', message)

    @gen.coroutine
    def ifttt_maker_request(self, event_type, message=None):
        """Make an IFTTT maker request"""
        http_client = AsyncHTTPClient()
        if event_type == 'notify':
            # Build event Json body
            body = urllib.parse.urlencode({'value1': message})
            url = 'https://maker.ifttt.com/trigger/{}/with/key/{}'.format(
                self.config.IFTTT_MAKER_EVENT_NAME, self.config.IFTTT_MAKER_KEY)
            logger.debug('IFTTT_MAKER: Pushing event: ' + url + ' with body: ' + body)
            res = yield http_client.fetch(url, method='POST', body=body)

            # Check result
            if res.code == 200:
                logger.debug('IFTTT_MAKER: Event pushed successfully')
            else:
                logger.debug('IFTTT_MAKER: Error pushing event: {}'.format(res))
        else:
            logger.error('Unsupported ifttt_maker request')
