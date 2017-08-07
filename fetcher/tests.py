#!/usr/bin/python3

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from tornado.escape import json_decode
from messages_pb2 import Tasks, Prices
import unittest
import server
from multiprocessing import Process
import requests
import time
from operator import itemgetter


class APIAirlineHandler(RequestHandler):
    available_departures = {
        '2018-12-04': {
            '2018-12-01': {'amount': '20001'},
            '2018-12-02': {'amount': '20002'},
            '2018-12-03': {'amount': '20003'},
            '2018-12-04': {'amount': '20004'},
            '2018-12-05': {'amount': '20005'},
            '2018-12-06': {'amount': '20006'},
            '2018-12-07': {'amount': '20007'}
        },
        '2020-01-04': {
            '2020-01-01': {'amount': '10001'},
            '2020-01-02': {'amount': '10002'},
            '2020-01-03': {'amount': '10003'},
            '2020-01-04': {'amount': '10004'},
            '2020-01-05': {'amount': '10005'},
            '2020-01-06': {'amount': '10006'},
            '2020-01-07': {'amount': '10007'}
        },
    }

    def post(self):
        request_data = json_decode(self.request.body)
        prices = list()
        for route in request_data['routes']:
            prices.append(
                self.available_departures.get(route['departure'], dict())
            )
        self.write({'data': {'min_prices': prices}})


class APIPriceHandler(RequestHandler):
    user_data = []

    def post(self):
        APIPriceHandler.user_data.append(self.request.body)

    def get(self):
        if APIPriceHandler.user_data:
            self.write(APIPriceHandler.user_data.pop(0))


class BaseServer:
    def __init__(self):
        self.process = Process(target=self.main)

    def main(self):
        raise Exception('Not implemented')

    def start(self):
        self.process.start()

    def terminate(self):
        self.process.terminate()


class APIServer(BaseServer):
    host = '127.0.0.1'
    port = 1081
    airline_api = 'http://%s:%s/airline' % (host, port)
    aeroraker_api = 'http://%s:%s/aeroraker/' % (host, port)

    def main(self):
        app = Application([
            (r"/airline", APIAirlineHandler),
            (r"/aeroraker/price/", APIPriceHandler)
        ])
        app.listen(self.port, address=self.host)
        IOLoop.current().start()


class FetcherServer(BaseServer):
    host = '127.0.0.1'
    port = 1080
    api = 'http://%s:%s' % (host, port)

    def main(self):
        app = Application([
            (r"/task", server.TaskHandler)
        ])
        app.listen(self.port, address=self.host)
        IOLoop.current().start()


class TestMain(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.api_server = APIServer()
        self.api_server.start()
        self.fetcher_server = FetcherServer()
        self.fetcher_server.start()
        time.sleep(2)

    def test_task_handler(self):
        testdata = [
            {
                'task_id': 112,
                'origin': 'MOW',
                'destination': 'HKT',
                'search_date_start': '2018-12-01',
                'search_date_end': '2018-12-01',
            },
            {
                'task_id': 345,
                'origin': 'HKT',
                'destination': 'MOW',
                'search_date_start': '2020-01-01',
                'search_date_end': '2020-01-01',
            },
        ]

        tasks = Tasks()
        for d in testdata:
            task = tasks.list.add()
            task.task_id = d['task_id']
            task.origin = d['origin']
            task.destination = d['destination']
            task.search_date_start = d['search_date_start']
            task.search_date_end = d['search_date_end']

        response_fetcher = requests.post(
            self.fetcher_server.api + '/task',
            data=tasks.SerializeToString()
        )
        self.assertEqual(response_fetcher.status_code, 200)

        time.sleep(5)

        fetcher_data = list()
        while True:
            response_api = requests.get(
                self.api_server.aeroraker_api + 'price/',
            )
            if response_api.status_code != 200 or not response_api.content:
                break
            prices = Prices()
            prices.ParseFromString(response_api.content)
            fetcher_data = fetcher_data + [
                dict(
                    amount=price.amount,
                    date=price.date,
                    task_id=price.task_id
                )
                for price in prices.list
            ]

        expected_data = [
            {'amount': 20001, 'date': '2018-12-01', 'task_id': 112},
            {'amount': 20002, 'date': '2018-12-02', 'task_id': 112},
            {'amount': 20003, 'date': '2018-12-03', 'task_id': 112},
            {'amount': 20004, 'date': '2018-12-04', 'task_id': 112},
            {'amount': 20005, 'date': '2018-12-05', 'task_id': 112},
            {'amount': 20006, 'date': '2018-12-06', 'task_id': 112},
            {'amount': 20007, 'date': '2018-12-07', 'task_id': 112},
            {'amount': 10001, 'date': '2020-01-01', 'task_id': 345},
            {'amount': 10002, 'date': '2020-01-02', 'task_id': 345},
            {'amount': 10003, 'date': '2020-01-03', 'task_id': 345},
            {'amount': 10004, 'date': '2020-01-04', 'task_id': 345},
            {'amount': 10005, 'date': '2020-01-05', 'task_id': 345},
            {'amount': 10006, 'date': '2020-01-06', 'task_id': 345},
            {'amount': 10007, 'date': '2020-01-07', 'task_id': 345}
        ]

        sorted_key = itemgetter('amount', 'date', 'task_id')
        self.assertEqual(
            sorted(fetcher_data, key=sorted_key),
            sorted(expected_data, key=sorted_key)
        )

    @classmethod
    def tearDownClass(self):
        self.api_server.terminate()
        self.fetcher_server.terminate()


if __name__ == '__main__':
    server.AIRLINE_API = APIServer.airline_api
    server.AERORAKER_API = APIServer.aeroraker_api
    unittest.main()
