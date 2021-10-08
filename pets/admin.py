from django.contrib import admin
from .models import *

admin.site.register(Pet)
admin.site.register(PetLocation)
admin.site.register(OwnerLocation)
admin.site.register(DetectiveLocation)
admin.site.register(Case)
admin.site.register(Request)
