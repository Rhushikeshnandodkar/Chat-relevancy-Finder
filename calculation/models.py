from django.db import models

# Create your models here.
class MachineModel(models.Model):
    machine_name = models.CharField(max_length=300, null=True, blank=True)
    machine_constant = models.IntegerField(null=True, blank=True)

class AreaCalculation(models.Model):
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE)
    process_name = models.CharField(max_length=300, null=True, blank=True)

class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    comment = models.CharField(max_length=300, null=True, blank=True)
    tag = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.comment