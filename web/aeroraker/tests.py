from django.test import TestCase
from django.core.urlresolvers import reverse
from aeroraker.models import Task, Price, City
import datetime
import json
from messages_pb2 import Prices


class TaskViewTests(TestCase):
    def test_response(self):
        city1 = City.objects.create(name='Winterfell', iata='WTF')
        city2 = City.objects.create(name='King\'s Landing', iata='KLN')
        tasks = list()
        tasks.insert(
            0,
            Task.objects.create(
                origin=city1,
                destination=city2,
                search_date_start=datetime.date(2018, 1, 1),
                search_date_end=datetime.date(2018, 1, 20)
            )
        )
        tasks.insert(
            0,
            Task.objects.create(
                origin=city2,
                destination=city1,
                search_date_start=datetime.date(2020, 1, 1),
                search_date_end=datetime.date(2020, 1, 20)
            )
        )
        response = self.client.get(reverse('aeroraker:task'))
        self.assertEqual(response.status_code, 200)
        objs = json.loads(response.content.decode())
        self.assertEqual(len(objs), len(tasks))
        for i, obj in enumerate(objs):
            self.assertEqual(obj['origin'], tasks[i].origin.name)
            self.assertEqual(obj['destination'], tasks[i].destination.name)
            self.assertEqual(
                obj['search_date_start'],
                tasks[i].search_date_start.strftime('%Y-%m-%d')
            )
            self.assertEqual(
                obj['search_date_end'],
                tasks[i].search_date_end.strftime('%Y-%m-%d')
            )


class PriceViewTests(TestCase):
    def test_handler(self):
        city1 = City.objects.create(name='Winterfell', iata='WTF')
        city2 = City.objects.create(name='King\'s Landing', iata='KLN')
        task = Task.objects.create(
            origin=city1,
            destination=city2,
            search_date_start=datetime.date(2018, 1, 1),
            search_date_end=datetime.date(2018, 1, 20)
        )

        prices = Prices()
        price = prices.list.add()
        price.amount = 10000
        price.date = '2018-01-03'
        price.task_id = task.id

        response = self.client.post(
            reverse('aeroraker:price'),
            data=prices.SerializeToString(),
            content_type='application/octet-stream'
        )
        self.assertEqual(response.status_code, 200)

        objs = Price.objects.all()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0].amount, 10000)
        self.assertEqual(objs[0].date, datetime.date(2018, 1, 3))
        self.assertEqual(objs[0].task.id, task.id)


class TaskDetailViewTests(TestCase):
    def test_response(self):
        city1 = City.objects.create(name='Winterfell', iata='WTF')
        city2 = City.objects.create(name='King\'s Landing', iata='KLN')
        task = Task.objects.create(
            origin=city1,
            destination=city2,
            search_date_start=datetime.date(2018, 1, 1),
            search_date_end=datetime.date(2018, 1, 20)
        )

        response = self.client.get(
            reverse('aeroraker:taskdetail', args=(task.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['task'], task)
