from celery import Celery
import celery_redis
import time

app = Celery('tasks', broker='redis://localhost:6379/0',
              backend="celery_redis.RedisBackend+redis://localhost:6379/0")

@app.task(name='test.add')
def add(x, y):
    time.sleep(1)
    return x + y

if __name__ == "__main__":
    r = add.delay(5, 4)
    result = r.get()
    print(result)
