from aeroraker.messages_pb2 import Tasks, Prices
from rest_framework import serializers
from aeroraker.models import Task, Price


class TasksProtobuf:
    def __init__(self):
        self.tasks = Tasks()

    def add(self, task):
        t = self.tasks.list.add()
        t.task_id = task.id
        t.origin = task.origin.iata
        t.destination = task.destination.iata
        t.search_date_start = task.search_date_start.strftime('%Y-%m-%d')
        t.search_date_end = task.search_date_end.strftime('%Y-%m-%d')

    def serialize(self):
        return self.tasks.SerializeToString()


class TaskModelSerializer(serializers.ModelSerializer):
    origin = serializers.CharField(source='origin.name')
    destination = serializers.CharField(source='destination.name')
    completed = serializers.CharField()
    url = serializers.CharField()

    class Meta:
        model = Task


class PricesProtobuf:
    def __init__(self):
        self.prices = Prices()

    def deserialize(self, data):
        self.prices.ParseFromString(data)
        objs = [
            Price(amount=p.amount, date=p.date, task_id=p.task_id)
            for p in self.prices.list
        ]
        return objs
