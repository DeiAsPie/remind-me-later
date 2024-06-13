from flask import Flask, render_template, request
from flask_restful import Resource, Api
from threading import Thread
from time import time, sleep
import heapq
import threading

app = Flask(__name__)
api = Api(app)

queue = []
queue_lock = threading.Lock()

def process_queue():
    while True:
        sleep(1)

class AddItem(Resource):
    def post(self):
        data = request.get_json()
        item = data.get('item')
        delay = data.get('delay')
        if not item or not isinstance(delay, int):
            return {'message': 'Invalid input'}, 400
        available_at = time() + delay
        with queue_lock:
            heapq.heappush(queue, (available_at, item))
        return {'message': 'Item added', 'item': item, 'delay': delay}, 200

class GetItems(Resource):
    def get(self):
        current_time = time()
        available_items = []
        with queue_lock:
            while queue and queue[0][0] <= current_time:
                _, item = heapq.heappop(queue)
                available_items.append(item)
        return {'items': available_items}, 200

@app.route('/')
def home():
   return render_template('index.html')

api.add_resource(AddItem, '/api/add')
api.add_resource(GetItems, '/api/items')

if __name__ == '__main__':
    thread = Thread(target=process_queue)
    thread.daemon = True
    thread.start()
    app.run(debug=True, host='0.0.0.0')
