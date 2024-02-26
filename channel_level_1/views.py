from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status

from channel_level_1.serializers import SegmentSerializer
from channel_level_1.models import Segment

from rest_framework.views import APIView
from rest_framework.decorators import api_view

import json
# from channel_level_1.circle_code import *
import numpy as np
import random

class SegmentList(APIView): # переименовать
    model_class = Segment
    serializer_class = SegmentSerializer
    # Возвращает список акций
    def get(self, request, format=None):
        with open('file.json', 'r') as f: # данный код надо переписать для коннекта с транспортным уровнем
            segments = json.load(f)
        print("ФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФФ")
        error_chance = 40
        loss_chance = "undefined"
        status_loss = "undefined"
        s = self._segments_to_packages(segments) # преобразование в биты
        s = self._encode(s) # кодирование
        s, status_mistake = self._do_mistake(s, error_chance) # создание ошибки
        s = self._decode(s) # декодирование
        self._packages_to_segments(s) # преобразование в человекочитаемый формат

        return Response([{
            "person": segments[0]["sender"],
            "text_before": segments[0]["payload"],
            "text_after": "undefined",
            "segment": s,
            "status_error": status_mistake,
            "status_loss": status_loss,
            "error_chance": error_chance,
            "loss_chance": loss_chance,
        }])

    def _output_data(self, data, text = ""):
        for i in data:
            print((1 if i else 0), end=", ")
        print(" - ", text)

    def _segments_to_packages(self, segments):
        data = []
        for x in bytes(segments[0]["payload"], "utf-8"):
            for y in "{0:b}".format(x):
                data.append(y=='1')
        self._output_data(data, "данные в виде битов")
        print(len(data), "длина данных, до кодирования")
        print("-------------------------")
        return data
    
    def _packages_to_segments(self, packages):
        # data_to_read = []
        # print(len(packages), "длина данных, после кодирования")
        # for i in range(7, len(packages)+1, 7):
        #     decoded_data, stat = self._decode(packages[i-7:i])
        #     print(decoded_data, stat)
        #     data_to_read.extend(decoded_data)
        #     # print(encoded_data, " encoded segment num {}".format(i/4))
        # print(data_to_read, " - read data")
        # return data_to_read
        return []

    def _encode(self, data):
        data_to_send = []
        for i in range(4, len(data)+1, 4):
            encoded_data = self._encode_4_7(data[i-4:i])
            data_to_send.extend(encoded_data)
            self._output_data(encoded_data)
        self._output_data(data_to_send, "закодированные данные")
        return data_to_send

    def _encode_4_7(self, data):
        el = data + [False, False, False]
        i = 0
        while i != 4:
            if el[i] == False:
                i += 1
                continue
            el[i:i+4] = np.logical_xor(el[i:i+4], [True, False, True, True])
        return data + el[4:7]
    
    def _decode(self, data):
        data_to_read = []
        for i in range(7, len(data)+1, 7):
            decoded_data, stat_err = self._decode_7_4(data[i-7:i])
            if stat_err:
                decoded_data = self._fix_mistake(data[i-7:i]) # чиним ошибку
                print("Here we fix the mistake:")
            data_to_read.extend(decoded_data)
            self._output_data(decoded_data)
        self._output_data(data_to_read, "раскодированные данные")
        return data_to_read

    def _decode_7_4(self, data):
        el = data.copy()
        i = 0
        while i != 4:
            if el[i] == False:
                i += 1
                continue
            el[i:i+4] = np.logical_xor(el[i:i+4], [True, False, True, True])
        
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
            data_copy[i:i+4] = np.logical_xor(data_copy[i:i+4], [True, False, True, True])
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
        print("Рандомная ошибка равна: ", random_index, ", возможно - ",  len(data), ", Статус ошибки:", stat)
        return data, stat