from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@localhost', 'admin')
from aeroraker.models import City
City.objects.create(name='Moscow', iata='MOW')
City.objects.create(name='Phuket', iata='HKT')
