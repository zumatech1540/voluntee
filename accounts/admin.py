from django.contrib import admin
from .models import User, County, Constituency, Ward, PollingStation
from .models import Donation
admin.site.register(User)
admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(Ward)
admin.site.register(PollingStation)
admin.site.register(Donation)