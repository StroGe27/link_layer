from django.db import models

class Segment(models.Model):
    sender = models.CharField(max_length=50, verbose_name="Имя отправителя")
    dispatch_time = models.DateTimeField(auto_now=False, verbose_name="Время отправки")
    payload = models.CharField(max_length=320, verbose_name="Полезная нагрузка") # здесь поставил ограничение на 320!!!