from django.db import models

# Create your models here.
class Destination(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)  # Allow null values
    longitude = models.FloatField(null=True, blank=True)  # Allow null values
    time = models.IntegerField()  # Assuming time is in minutes
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "destinations"
