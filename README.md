Celery Redis Result Backend
---------------------------

This package extends the Celery redis result backend to use pubsub for waiting
for task results to be published.

It is currently in an experimental state, and not well tested.


To use it, set your backend as follows:

```
CELERY_RESULT_BACKEND=celery_redis.RedisBackend+redis://localhost:6379/0
```


Known issues
============

- There is a very window between checking if the result has already been 
  published to the key, and subscribing the pubsub listener during which the
  result could be published (and hence missed)

- python-redis currently doesn't support setting a timeout on the `pubsub.listen` 
  method. If a timeout is specified in the call to `result.get` then polling is
  used to check for messages at the specified `interval`.


Running the test
================

There is currently only a very rudimentary test case.

To try it, start the celery worker `celery worker -A test.app` and run the test
script `python test.py`.