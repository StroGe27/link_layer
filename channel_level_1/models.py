from django.db import models

class Segment(models.Model):
    segment_number = models.IntegerField(verbose_name="Номер сегмента")
    amount_segments = models.IntegerField(verbose_name="Общее число сегментов")
    segment_data = models.CharField(max_length = 50, verbose_name="Тело сегмента")
    dispatch_time = models.IntegerField(verbose_name="Время отправки сообщения")
    sender = models.CharField(max_length=50, verbose_name="Имя отправителя")
