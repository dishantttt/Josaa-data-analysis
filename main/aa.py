from django.db import models

# Create your models here.


class data(models.Model):
    institute = models.CharField(max_length=300)
    program = models.CharField(max_length=500)
    seat_type = models.CharField(max_length=300)
    gender = models.CharField(max_length=300)
    opening_rank = models.IntegerField()
    closing_rank = models.IntegerField()
    year = models.IntegerField()
    roundNo = models.IntegerField()
    preparatory = models.BooleanField(default=False)
    institute_type = models.CharField(max_length=300, default='GFTI')
