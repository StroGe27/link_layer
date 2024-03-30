from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from requests import post
# from rest_framework import status

from channel_level_1.serializers import SegmentSerializer
from channel_level_1.models import Segment

from rest_framework.views import APIView
from rest_framework.decorators import api_view

from drf_yasg.utils import swagger_auto_schema
import random

import requests

class SegmentList(APIView): # переименовать
    model_class = Segment
    serializer_class = SegmentSerializer

    @swagger_auto_schema(
        request_body=SegmentSerializer,  # Описывает структуру запроса
        responses={200: SegmentSerializer},  # Описывает структуру ответа
        operation_description = "Произвести действия с сегментом и отправить на Транспортный уровень"
    )
    def post(self, request, format=None):
        error_chance = 40
        loss_chance = 33

        request = request.data
        s = self._segments_to_packages(request) # преобразование в биты
        s = self._encode(s) # кодирование
        s, status_mistake = self._do_mistake(s, error_chance) # создание ошибки
        status_loss = self._do_loss(loss_chance) # создание потери
        s = self._decode(s) # декодирование
        payload = self._packages_to_segments(s) # преобразование в человекочитаемый формат

        if status_loss:
            return Response([{
                "info": "Сообщение отправлено!",
                "segment_data": payload
            }])
        
        
        data_to_send = {
            "amount_segments": request["amount_segments"],
            "segment_number": request["segment_number"],
            "sender": request["sender"],
            "segment_data": payload,
            "dispatch_time": request["dispatch_time"]
            }
    
        print("Отправляемые данные: \n", data_to_send)

        requests.post("http://172.20.10.3:8000/postMessage/", json=data_to_send)

        return Response([{
                "info": "Сообщение отправлено!",
                "segment_data": payload
            }])
    
    @swagger_auto_schema(
        responses={200: SegmentSerializer},  # Описывает структуру ответа
        operation_description = "Проверка работы"
    )
    def get(self, request, format=None):
        return Response([{
            "status": "ok",
        }])

    # данная функция нужна только для тестирования
    def _test_add_error_for_kafka(what_is_error, status_loss, request, payload):
        # 0 - ошибка в любом месте
        # 1 - ошибка только в начале сегмента
        # 2 - ошибка в середине сегмента (не в 1ом и не в последнем)
        # 3 - ошибка только в конце сегмента

        if status_loss:
            return Response([{
                "info": "Сообщение отправлено!",
                "segment_data": payload
            }])
        
        if status_loss and request["segment_number"] == 0:
            print("Произошла ошибка в сегмента с номером: ", request["segment_number"])
            return Response([{
                "info": "Сообщение отправлено!",
                "segment_data": payload
            }])

        if status_loss and request["amount_segments"]-1 != request["segment_number"] and request["segment_number"] != 0:
            print("Произошла ошибка в сегмента с номером: ", request["segment_number"])
            return Response([{
                "info": "Сообщение отправлено!",
                "segment_data": payload
            }])
    
        if status_loss and request["segment_number"] == request["amount_segments"]-1:
            print("Произошла ошибка в сегмента с номером: ", request["segment_number"])
            return Response([{
                "info": "Сообщение отправлено!",
                "segment_data": payload
            }])

    def _output_data(self, data, text = ""):
        for i in data:
            print((1 if i else 0), end=", ")
        print(" - ", text)

    def _segments_to_packages(self, segments):
        data = []
        # print(segments.)
        # payload_value = segments.json()["payload"]
        for x in segments["segment_data"].encode('utf-8'):
            # binary_value = format(ord(x), '08b')
            for y in "{0:08b}".format(x):
                data.append(y=='1')
        # self._output_data(data, "данные в виде битов")
        # print(len(data), "длина данных, до кодирования")
        # print("-------------------------")
        return data
    
    def _packages_to_segments(self, packages):
        data_to_read = []
        for i in range(8, len(packages)+1, 8):
            tmp = 0
            for j in range(i-1, i-9, -1):
                tmp += packages[j]*pow(2, 7-j%8)
            data_to_read.append(chr(tmp))
        return ''.join(data_to_read)

    def _encode(self, data):
        data_to_send = []
        for i in range(4, len(data)+1, 4):
            encoded_data = self._encode_4_7(data[i-4:i])
            data_to_send.extend(encoded_data)
            # self._output_data(encoded_data)
        # self._output_data(data_to_send, "закодированные данные")
        return data_to_send

    def _encode_4_7(self, data):
        el = data + [False, False, False]
        i = 0
        while i != 4:
            if el[i] == False:
                i += 1
                continue
            el[i:i+4] = self.logical_xor(el[i:i+4], [True, False, True, True])
        return data + el[4:7]
    
    def _decode(self, data):
        data_to_read = []
        for i in range(7, len(data)+1, 7):
            decoded_data, stat_err = self._decode_7_4(data[i-7:i])
            if stat_err:
                decoded_data = self._fix_mistake(data[i-7:i]) # чиним ошибку
                # print("Here we fix the mistake:")
            data_to_read.extend(decoded_data)
            # self._output_data(decoded_data)
        # self._output_data(data_to_read, "раскодированные данные")
        return data_to_read

    def _decode_7_4(self, data):
        el = data.copy()
        i = 0
        while i != 4:
            if el[i] == False:
                i += 1
                continue
            el[i:i+4] = self.logical_xor(el[i:i+4], [True, False, True, True])
        
        return data[0:4], el != [False, False, False, False, False, False, False]

    def _find_syndrom(self, data):
        table_whith_syndrome = [
            [False, False, True],
            [False, True, False],
            [True, False, False],
            [False, True, True],
            [True, True, False],
            [True, True, True],
            [True, False, True]
            ]
        for i in range(len(table_whith_syndrome)):
            if table_whith_syndrome[i] == data:
                return 6-i

    def _fix_mistake(self, data):
        data_copy = data.copy()
        i = 0 # находим положение нашей ошибки:
        while i != 4:
            if data_copy[i] == False:
                i += 1
                continue
            data_copy[i:i+4] = self.logical_xor(data_copy[i:i+4], [True, False, True, True])
        place_with_mistake = self._find_syndrom(data_copy[4:7])
        data[place_with_mistake] = data[place_with_mistake] ^ True # Иправляем её
        return data[0:4]

    def _do_mistake(self, data, error_chance):
        random_number = random.randint(0, 100)
        random_index = random.randint(0, len(data) - 1)
        stat = False
        if random_number <= error_chance:
            stat = True
            data[random_index] = data[random_index] ^ True
        # print("Рандомная ошибка равна: ", random_index, ", возможно - ",  len(data), ", Статус ошибки:", stat)
        return data, stat
    
    def _do_loss(self, loss_chance):
        return random.randint(0, 100) <= loss_chance
    
    def logical_xor(self, a, b):
        return [a[i] != b[i] for i in range(len(a))]