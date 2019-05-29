import celery
import threading
import os


class ThreadDelay:
    @staticmethod
    def task(func):
        def run_later(*argv):
            task = threading.Thread(target=func, args=argv)
            task.start()
        func.delay = run_later
        return func


app = ThreadDelay()
if os.getenv('BROKER'):
    print("Using" + os.getenv('BROKER'))
    app = celery.Celery('tasks', broker=os.getenv('BROKER'))
