from __future__ import absolute_import

import time

from celery import states
from celery.backends.redis import RedisBackend as _RedisBackend
from celery.exceptions import TimeoutError


class RedisBackend(_RedisBackend):
    def wait_for(self, task_id,timeout=None, interval=0.5, no_ack=True, propagate=True):
    
        timeout = timeout or 600  # don't take any chance
        def rread(key):
          meta = self.client.get(key)
          if meta:
            meta = self.decode(meta)
            if meta['status'] not in states.READY_STATES:
              meta = None
          return meta
            
        key = self.get_key_for_task(task_id)
        p = self.client.pubsub(ignore_subscribe_messages=True)
        p.subscribe(key)
        meta = rread(key)

        if not meta:
            time_elapsed = 0.0 
            while True:
                start = time.time()
                message = p.get_message(timeout=timeout)
                interval2 = time.time() - start  #use the real interval
                if message:
                    break
                
                time_elapsed += interval2
                if time_elapsed >= timeout:
                    p.unsubscribe()
                    p.close()
                    meta = rread(key)
                    if meta:
                       return meta  # in case we missed the message
                    raise TimeoutError('The operation timed out.')

            assert message['type'] == 'message'
            assert message['channel'] == key
            meta = self.decode(message['data'])
        p.unsubscribe()
        p.close()
        return meta

