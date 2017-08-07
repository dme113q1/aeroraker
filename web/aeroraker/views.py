from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from aeroraker.models import City, Task
from aeroraker.forms import TaskForm
from aeroraker.serializers import TasksProtobuf, TaskModelSerializer, \
    PricesProtobuf
from aeroraker.config import FETCHER_API
import requests
from rest_framework import generics
from django.views.generic import View, DetailView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class MainView(FormView):
    form_class = TaskForm
    success_url = reverse_lazy('aeroraker:main')
    template_name = 'aeroraker/main.html'

    def form_valid(self, form):
        task = Task.objects.create(
            origin=City.objects.get(id=form.cleaned_data['origin']),
            destination=City.objects.get(id=form.cleaned_data['destination']),
            search_date_start=form.cleaned_data['search_date_start'],
            search_date_end=form.cleaned_data['search_date_end']
        )
        tasks_protobuf = TasksProtobuf()
        tasks_protobuf.add(task)

        if form.cleaned_data['roundtrip']:
            task = Task.objects.create(
                origin=City.objects.get(id=form.cleaned_data['destination']),
                destination=City.objects.get(id=form.cleaned_data['origin']),
                search_date_start=form.cleaned_data['search_date_start'],
                search_date_end=form.cleaned_data['search_date_end']
            )
            tasks_protobuf.add(task)

        requests.post(FETCHER_API + '/task', data=tasks_protobuf.serialize())
        return super().form_valid(form)


class TaskView(generics.ListAPIView):
    queryset = Task.objects.extra(order_by=['-ts'])
    serializer_class = TaskModelSerializer


class PriceView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        prices = PricesProtobuf().deserialize(request.body)
        list(map(lambda obj: obj.save(), prices))
        return JsonResponse({'result': 'ok'})


class TaskDetailView(DetailView):
    model = Task
    template_name = 'aeroraker/taskdetail.html'
