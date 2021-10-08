from django.contrib.gis.db import models
from accounts.models import Account
from .validators import FileValidator
import os, secrets

validate_file = FileValidator(max_size=1024 * 5000,
                             content_types=('image/jpeg','image/png','image/gif','image/tiff','application/x-empty',))

def image_path_handler(instance, filename):
    fn, ext = os.path.splitext(filename)
    #Create a random filename using hash function
    name = secrets.token_hex(20)
    return "pet_{id}/{name}.png".format(id=instance.id,name=name)

pet_statuses = {
    0 : 'Missing',
    1 : 'Found Alive',
    2 : 'Found Dead',
    3 : 'Alive',
    4 : 'Dead'
}

class Pet(models.Model):
    owner = models.ForeignKey(Account,on_delete=models.CASCADE)
    name =  models.CharField(max_length=50)
    description =  models.CharField(max_length=500)
    last_seen =  models.CharField(max_length=500)
    animal = models.CharField(max_length=50)
    picture = models.ImageField(upload_to=image_path_handler,validators=[validate_file],null=True,blank=True)
    status = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


location_types = {
    0 : 'Missing Location',
    1 : 'Found Loctation',
    2 : 'Held Location'
}

class PetLocation(models.Model):
    pet = models.ForeignKey(Pet,on_delete=models.CASCADE)
    location_type = models.IntegerField(default=0)
    point = models.PointField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['pet','location_type'], name='unique_pet_locationtype')
        ]

class OwnerLocation(models.Model):
    owner = models.ForeignKey(Account,on_delete=models.CASCADE)
    point = models.PointField()

class DetectiveLocation(models.Model):
    detective = models.ForeignKey(Account,on_delete=models.CASCADE)
    point = models.PointField()

class Request(models.Model):
    detective = models.ForeignKey(Account,on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet,on_delete=models.CASCADE)
    accepted = models.BooleanField(default=True)
    description = models.CharField(max_length=500)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['pet','detective'], name='unique_request_pet_detective')
        ]

class Case(models.Model):
    detective = models.ForeignKey(Account,on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet,on_delete=models.CASCADE)
    request =  models.ForeignKey(Request,on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['pet','detective'], name='unique_case_pet_detective')
        ]
