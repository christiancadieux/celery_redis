from __future__ import absolute_import

import time

from celery.backends.redis import RedisBackend as _RedisBackend
from celery.exceptions import TimeoutError


class RedisBackend(_RedisBackend):
    def wait_for(self, task_id,
                 timeout=None, propagate=True, interval=0.5, no_ack=True,
                 on_interval=None):
        key = self.get_key_for_task(task_id)
        meta = self.client.get(key)
        if not meta:
            p = self.client.pubsub(ignore_subscribe_messages=True)
            p.subscribe(key)
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
            p.unsubscribe()
            p.close()
            assert message['type'] == 'message'
            assert message['channel'] == key
            meta = message['data']
        return self.decode(meta)
