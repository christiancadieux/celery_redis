from __future__ import absolute_import

import time

from celery import states
from celery.backends.redis import RedisBackend as _RedisBackend
from celery.exceptions import TimeoutError


class RedisBackend(_RedisBackend):
    def wait_for(self, task_id,
                 timeout=None, interval=0.5, no_ack=True, on_interval=None):
        key = self.get_key_for_task(task_id)
        p = self.client.pubsub(ignore_subscribe_messages=True)
        p.subscribe(key)
        meta = self.client.get(key)
        if meta:
            meta = self.decode(meta)
            if meta['status'] not in states.READY_STATES:
                meta = None
        if not meta:
            if timeout:
                time_elapsed = 0.0
                while True:
                    message = p.get_message()
                    if message:
                        break
                    if on_interval:
                        on_interval()
                    # avoid hammering the CPU checking status.
                    time.sleep(interval)
                    time_elapsed += interval
                    if time_elapsed >= timeout:
                        raise TimeoutError('The operation timed out.')
            else:
                message = next(p.listen())
            assert message['type'] == 'message'
            assert message['channel'] == key
            meta = self.decode(message['data'])
        p.unsubscribe()
        p.close()
        return meta
