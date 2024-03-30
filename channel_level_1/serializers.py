from channel_level_1.models import Segment
from rest_framework import serializers

class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Segment
        # Поля, которые мы сериализуем
        fields = [
            "segment_number",
            "amount_segments",
            "segment_data",
            "dispatch_time",
            "sender"
        ]