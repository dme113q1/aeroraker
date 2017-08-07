from django.db import models
from django.core.urlresolvers import reverse


class City(models.Model):
    name = models.CharField(max_length=50)
    iata = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    ts = models.DateTimeField(auto_now_add=True)
    origin = models.ForeignKey(City, related_name='city_origin_set')
    destination = models.ForeignKey(City, related_name='city_destination_set')
    search_date_start = models.DateField()
    search_date_end = models.DateField()

    @property
    def completed(self):
        total_days = 1 + (self.search_date_end - self.search_date_start).days
        percent = 100 * min(self.price_set.count() / total_days, 1)
        return '%s%%' % int(percent)

    @property
    def url(self):
        return reverse('aeroraker:taskdetail', args=[self.id])

    def __str__(self):
        return str(self.id)


class Price(models.Model):
    amount = models.PositiveIntegerField()
    date = models.DateField()
    task = models.ForeignKey(Task)

    def __str__(self):
        return str(self.id)
