from flask import Flask
import time
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(2)

app = Flask(__name__)


@app.route('/synchronize')
def update_redis():
    executor.submit(do_update)
    return 'ok'


def do_update():
    time.sleep(3)
    print('start update')


if __name__ == '__main__':
    app.run()
