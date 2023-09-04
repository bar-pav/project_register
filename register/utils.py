import json
import pandas as pd
from django.db.models import Q
from .models import Equipment, EndPoint, Port, Communication, InterfaceType, Consumer

import re


source_file = 'register/source.xlsx'


class UnknownConnectionPoint(Exception):
    """ Неизвестная точка подключения"""


class RedundantPortExist(Exception):
    """ В таблице имеется больше портов для данного оборудования, чем возможно."""


class UndefinedCommunication(Exception):
    pass


class CreateEquipment:
    """ Извлекаем данные из .xlsx файла.
        Порядок чтения:
            Название
            Расположение | ИП
            Куда подключен групповой поток
            Система
            Трасса
            -
            -
            -
            номер канала    | связь     | направление    | название платы    | рамка

            Метод класса берет ИП (либо, если не указан, берет/создает по умолчанию) и задает такой же для "Куда подключен групповой поток", если создается новая точка.


        Dataframe attribute axes is the list with data like this:
            [RangeIndex(start=0, stop=9, step=1), Index(['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3'], dtype='object')]
            Index == columns.
            Columns are numbered from 0.
    """
    NUM_OF_PORTS = 30

    def __init__(self, file=None, test=True):
        self.file = file
        self.test = test
        self.errors = []
        self.sp_re = re.compile(r"(СП\d+)[- ]*?((?:Р|рамка)?\d+)[- ]*?((?:М|место)?\d+)", re.I)
        self.sp_re_simple = re.compile(r"(\d+).*?(\d+).*?(\d+)")
        self.interface_type_group = InterfaceType.objects.get(type__iexact='поток')
        self.interface_type_chanel = InterfaceType.objects.get(type__iexact='канал')
        try:
            self.df = pd.read_excel(file, dtype="object")
        except Exception as e:
            self.errors.append(e)
            self.df = None
        if self.df is not None and not self.df.empty:
            self.name = self.get_name()
            self.location = self.get_location()
            self.endpoint = self.get_endpoint(self.df[1][1], default=True)
            self.connected_to = self.get_frame_sp(self.df[0][2])
            self.frame_name = CreateEquipment.get_frame_name(self.df[0][2])
            self.system = self.df[0][3].strip() if not pd.isna(self.df[0][3]) else None  # TODO Continue. Create method .get_system()
            self.route = self.df[0][4].strip() if not pd.isna(self.df[0][4]) else None # TODO
            self.frame_info = self.df[4][7].strip() if not pd.isna(self.df[4][7]) else None
            self.note = self.get_json_note()
            self.equipment = self.get_existed_equipment(self.name, 'E') or self.create_equipment(self.name,
                                                                                                           self.endpoint,
                                                                                                           self.location,
                                                                                                           'E',
                                                                                                           None,
                                                                                                           self.note)
            self.group_port = self.get_group_port(connected_to=self.connected_to)
            self.ports = self.get_ports()
            print(self.equipment)

    def get_name(self):
        return self.df[0][0].strip()

    def get_location(self):
        return self.df[0][1].strip()

    def get_endpoint(self, code=None, default=False):
        if not pd.isna(code):
            endpoint_instance = EndPoint.objects.filter(code__iexact=code)
            if endpoint_instance:
                return endpoint_instance.first()
            else:
                return self.create_endpoint(code)
        elif default:
            return self.get_or_create_default_endpoint()

    def create_endpoint(self, code, name=None, note=None):
        endpoint = EndPoint.objects.create(name=name, code=code, note=note)
        endpoint.save()
        print('Create endpoint:', endpoint)
        return endpoint

    def get_or_create_default_endpoint(self):
        default_name = 'vitebsk_endpoint'
        default_code = '1'
        default_note = None
        endpoint = EndPoint.objects.get(code__iexact=default_code)
        if endpoint:
            return endpoint
        else:
            endpoint = self.create_endpoint(default_code, default_name, default_note)
            endpoint.save()
            print('Create default endpoint:', endpoint)
            return endpoint

    @staticmethod
    def get_existed_equipment(name, equipment_type):
        equipment = Equipment.objects.filter(name__iexact=name).filter(type=equipment_type).first()
        if equipment:
            return equipment

    def create_equipment(self, name, endpoint, location, equipment_type, endpoint_opposite=None, note=None):
        equipment = Equipment.objects.create(name=name, endpoint=endpoint, location=location, type=equipment_type, endpoint_opposite=endpoint_opposite, note=note)
        equipment.save()
        print('Create equipment:', equipment)

        return equipment

    def get_frame_sp(self, to):
        connected_to = to
        print("Try get connected_to", connected_to)
        if pd.isna(connected_to):
            return None
        if "СП" in connected_to or "сп" in connected_to:
            connected_to.strip()
            re_result = self.sp_re_simple.findall(connected_to)
            print(re_result)
            sp = f'СП{re_result[0][0]}'
            print("СП:", sp)
            sp_port = f"Р{re_result[0][1]} М{re_result[0][2]}"
            print("СП порт:", sp_port)

            existed = self.get_existed_equipment(sp, 'F')
            if existed:
                sp_ports = Port.objects.filter(equipment=existed)
                if sp_ports:
                    sp_port_instance = sp_ports.get(port_name__iexact=sp_port)
                    if sp_port_instance:
                        return sp_port_instance
                sp_port_instance = Port.objects.create(equipment=existed,
                                                       port_name=sp_port,
                                                       interface_type=self.interface_type_group,
                                                       media_type='E',
                                                       note=None)
                sp_port_instance.save()
                print('Create port:', sp_port_instance)
                return sp_port_instance
            else:
                new_sp = self.create_equipment(name=sp, endpoint=self.endpoint, location='?', equipment_type='F')
                new_sp.save()
                print('Create SP:', new_sp)
                sp_port_instance = Port.objects.create(equipment=new_sp,
                                                       port_name=sp_port,
                                                       interface_type=self.interface_type_group,
                                                       media_type='E',
                                                       note=None)
                sp_port_instance.save()
                print('Create port:', sp_port_instance)
                return sp_port_instance
        else:
            self.errors.append(UnknownConnectionPoint(f"Ошибка. Неизвестная точка подключения '{connected_to}'."))

    @staticmethod
    def get_frame_name(to):
        if pd.isna(to):
            return None
        else:
            if to is str:
                return to.strip()
            else:
                return str(to)

    def get_group_port(self, connected_to):
        if self.equipment:
            group_port = Port.objects.filter(equipment=self.equipment).filter(port_name="group_port")
            if len(group_port) > 1:
                self.errors.append(RedundantPortExist(f"В базе есть лишние порты для оборудования 'id={self.equipment.id}, {self.equipment}'"))
                return
            elif len(group_port) == 1:
                group_port = group_port.first()
            else:
                group_port = Port.objects.create(port_name='group_port',
                                                 equipment=self.equipment,
                                                 interface_type=self.interface_type_group,
                                                 media_type='E',
                                                 note=None,
                                                 frame_name=self.frame_name)
                group_port.save()
            if connected_to:
                group_port.connect_to(connected_to)
                group_port.save()
            return group_port

    def get_json_note(self):
        note_dict = {
            "Система": self.system,
            "Трасса": self.route,
            "Порядок на рамках": self.frame_info,
        }
        return json.dumps(note_dict)

    # Update location and note about equipment.
    def update_equipment(self):
        changed = False
        if self.equipment.location != self.location:
            self.equipment.location = self.location
            changed = True
        if self.note and self.equipment.note != self.note:
            self.equipment.note = self.note
            changed = True
        if changed:
            self.equipment.save()

    # def get_system(self):

    def get_port_or_create(self, port_name, equipment, interface_type):
        port = Port.objects.filter(port_name__iexact=port_name).filter(equipment=equipment).first()
        if port:
            return port
        else:
            port = Port.objects.create(port_name=port_name,
                                       equipment=equipment,
                                       interface_type=interface_type,
                                       media_type='E',
                                       note=None)
            port.save()
            return port

    def get_or_create_consumer(self, name):
        consumer = Consumer.objects.filter(name__iexact=name)
        if consumer:
            return consumer.first()
        else:
            consumer = Consumer.objects.create(name=name, telephone=None, note=None)
            consumer.save()
            return consumer

    def get_communication_or_create(self, communication_name, direction, communication_type, consumer=None):
        if consumer is None:
            consumer = 'test consumer'
        else:
            pass  # TODO get_consumer()

        direction_from = None
        direction_to = None
        if not pd.isna(direction):
            directions = str(direction).split('-')
            if len(directions) > 1:
                direction_from = directions[0]
                direction_to = directions[-1]
            elif len(directions) == 1:
                direction_to = directions[0]
                direction_from = '1'

        if direction_from:
            direction_from = self.get_endpoint(direction_from)
        if direction_to:
            direction_to = self.get_endpoint(direction_to)

        consumer = self.get_or_create_consumer(consumer)

        communication = Communication.objects.filter(name__iexact=communication_name).filter(communication_type=communication_type).filter(consumer=consumer)
        # if direction_to:
        #     communication = communication.filter(direction_to=direction_to)
        # if direction_from:
        #     communication = communication.filter(direction_from=direction_from)

        if len(communication) == 1:
            return communication.first()
        elif not communication:
            communication = Communication.objects.create(name=communication_name,
                                                         direction_from=direction_from if direction_from else None,
                                                         direction_to=direction_to if direction_to else None,
                                                         communication_type = communication_type,
                                                         consumer=consumer)
            communication.save()
            return communication
        else:
            self.errors.append(UndefinedCommunication(f"Неопределенная связь для параметров: {communication_name}, {direction_from}, {direction_to}, {consumer}, {self.interface_type_chanel}."))

    def get_frame(self, equipment_name):
        frame = self.get_existed_equipment(equipment_name, 'F')
        if frame:
            return frame
        else:
            frame = self.create_equipment(name=equipment_name, endpoint=self.endpoint, location='?', equipment_type='F')
            frame.save()
            return frame

    def get_ports(self):
        for row in range(8, len(self.df)):
            port_num = self.df.iloc[row][0]
            communication_name = self.df.iloc[row][1]
            direction = self.df.iloc[row][2]
            board_name = self.df.iloc[row][3]
            frame_port_name = self.df.iloc[row][4]
            note_dict = {'Плата': board_name}
            port = self.get_port_or_create(port_num, self.equipment, self.interface_type_chanel)
            consumer = None
            communication = None
            if not pd.isna(communication_name):
                communication = self.get_communication_or_create(communication_name, direction, self.interface_type_chanel, consumer)
                port.communication = communication
            # frame = self.get_frame(self.equipment.name)  # Get instance of frame as record in table Equipment
            frame = self.get_frame_name(frame_port_name)  # Get instance of frame as record in table Equipment
            # frame_port = self.get_port_or_create(frame_port_name, frame, self.interface_type_chanel)
            # frame_port.communication = communication
            # port.connect_to(frame_port)
            port.frame_name = frame
            port.note = json.dumps(note_dict)
            port.save()
            print(port_num, communication, direction, board_name, frame)


# def find_column_id_with_contracts(df):
#
#     for row_id in range(0, len(df)):
#         for ind, j in enumerate(df.iloc[row_id]):
#             # if type(j) is str and (j.find('№') >= 0 or j.find('Дог') >= 0):
#             if type(j) is str and (re.findall(r'№ *(\d{0,4}/\d{0,3})', j)):
#                 return ind
#
#
#
#


# e = CreateEquipment(source_file)

def print_file(file):
    print(pd.read_excel(file, dtype="object"))
