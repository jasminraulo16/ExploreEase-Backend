from django.db import models

# Create your models here.
class Destination(models.Model):
    name = models.CharField(max_length=255)
    time = models.IntegerField()  # Assuming time is in minutes
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "destinations"
