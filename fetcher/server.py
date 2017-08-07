#!/usr/bin/python3

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_encode, json_decode
from messages_pb2 import Tasks, Prices
from datetime import datetime, timedelta

AIRLINE_API = 'https://www.aeroflot.ru/sb/booking/api/app/search/v2'
AERORAKER_API = 'http://web/aeroraker/'


class Session:
    def __init__(self, tasks):
        self.tasks = {t.task_id: self.generate_route(t) for t in tasks.list}
        self.client = AsyncHTTPClient()
        self.airline_payload = {
            'cabin': 'econom',
            'award': False,
            'country': 'ru',
            'adults': 1,
            'children': 0,
            'infants': 0,
            'combined': False,
            'coupons': [],
            'lang': 'ru',
            'extra': {},
            'client': {
                'ga_client_id': '',
                'loyality_id': '',
                'loyality_level': ''
            }
        }

    @gen.coroutine
    def start(self):
        while True:
            tasks_to_exec = list()
            self.airline_payload['routes'] = list()
            for task_id, generator in self.tasks.items():
                route = next(generator, None)
                if route:
                    tasks_to_exec.append(task_id)
                    self.airline_payload['routes'].append(route)
            if not tasks_to_exec:
                break
            response = yield self.get_airline_data()
            if response.code != 200:
                continue
            yield self.process_airline_data(response.body, tasks_to_exec)

    @gen.coroutine
    def process_airline_data(self, raw_body, tasks_to_exec):
        body = json_decode(raw_body)
        for idx, task_id in enumerate(tasks_to_exec):
            prices = Prices()
            for date, price_info in body['data']['min_prices'][idx].items():
                price = prices.list.add()
                price.amount = int(price_info['amount'])
                price.date = date
                price.task_id = task_id
            yield self.client.fetch(
                AERORAKER_API + 'price/',
                method='POST',
                body=prices.SerializeToString(),
                headers={'Content-Type': 'application/octet-stream'}
            )

    @gen.coroutine
    def get_airline_data(self):
        response = yield self.client.fetch(
            AIRLINE_API,
            method='POST',
            body=json_encode(self.airline_payload),
            headers={'Content-Type': 'application/json'}
        )
        return response

    @staticmethod
    def generate_route(task):
        search_date_start = datetime.strptime(
            task.search_date_start, '%Y-%m-%d'
        )
        search_date_end = datetime.strptime(
            task.search_date_end, '%Y-%m-%d'
        )
        if search_date_start > search_date_end:
            raise StopIteration

        route = {'origin': task.origin, 'destination': task.destination}

        days = (search_date_end - search_date_start).days
        for delta in range(3, days + 4, 7):
            departure = search_date_start + timedelta(days=delta)
            route['departure'] = departure.strftime("%Y-%m-%d")
            yield route.copy()


class TaskHandler(RequestHandler):
    def post(self):
        tasks = Tasks()
        tasks.ParseFromString(self.request.body)
        session = Session(tasks)
        IOLoop.current().spawn_callback(session.start)
        self.write("Tasks were accepted")


if __name__ == '__main__':
    app = Application([(r"/task", TaskHandler)])
    app.listen(1080)
    IOLoop.current().start()
