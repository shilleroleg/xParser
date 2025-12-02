import re
from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd

from xml_reader import XmlReader
from ideal_equipments import ideal_breaker as ib
from tools.logger import log


base_voltage_data = dict(mRID=['10000643-0000-0000-c000-0000006d746c', '1000068b-0000-0000-c000-0000006d746c',
                               '10000679-0000-0000-c000-0000006d746c', '77ffe719-31e0-4297-a320-58daaf45692a',
                               '1000066d-0000-0000-c000-0000006d746c', '1000066e-0000-0000-c000-0000006d746c',
                               '1000065c-0000-0000-c000-0000006d746c', '10000655-0000-0000-c000-0000006d746c',
                               '10000649-0000-0000-c000-0000006d746c', '1000063d-0000-0000-c000-0000006d746c',
                               '10000691-0000-0000-c000-0000006d746c', '3b1ca0c1-2eca-4b2e-b2e6-fcdb2dfec10a',
                               'e496e8ef-4ce8-4da5-8fbb-bcfb9097d9d1', '10000680-0000-0000-c000-0000006d746c',
                               '10000662-0000-0000-c000-0000006d746c', 'd1d0fee8-9a16-4fde-88ec-e300bf1ce4c2',
                               '10000619-0000-0000-c000-0000006d746c', '10000613-0000-0000-c000-0000006d746c',
                               '1000064f-0000-0000-c000-0000006d746c', 'e20d983f-4499-4fc9-896e-b9b46bc16c21',
                               '10000601-0000-0000-c000-0000006d746c', '100005fb-0000-0000-c000-0000006d746c',
                               '100012eb-0000-0000-c000-0000006d746c', '100005f5-0000-0000-c000-0000006d746c',
                               '100005ef-0000-0000-c000-0000006d746c', '100005e9-0000-0000-c000-0000006d746c',
                               '10000637-0000-0000-c000-0000006d746c', '1000062b-0000-0000-c000-0000006d746c',
                               '10000625-0000-0000-c000-0000006d746c', '1000067f-0000-0000-c000-0000006d746c',
                               '1000061f-0000-0000-c000-0000006d746c', '1000065b-0000-0000-c000-0000006d746c',
                               'f8af8aae-f46d-487b-b97d-6d07e18486b7', '29d3607d-5171-4edf-bf59-1a18504d6eb9',
                               '10000631-0000-0000-c000-0000006d746c', '0ab6ada6-096a-482d-bfa3-c195c4181eae',
                               '10000697-0000-0000-c000-0000006d746c'],
                         name=['1150 кВ', '750 кВ', '500 кВ', '±500 кВ', '400 кВ', '±400 кВ', '330 кВ', '220 кВ',
                               '150 кВ', '110 кВ', '87 кВ', '85 кВ', '67 кВ', '60 кВ', '35 кВ', '30 кВ', '27,5 кВ',
                               '24 кВ', '20 кВ', '19 кВ', '18 кВ', '15.75 кВ', '15 кВ', '13.8 кВ', '11 кВ', '10.5 кВ',
                               '10 кВ', '6.6 кВ', '6.3 кВ', '6 кВ', '3.15 кВ', '3 кВ', '1 кВ', '0.66 кВ', '0.4 кВ',
                               '0.3 кВ', 'Нейтраль'],
                         nominalVoltage=[1150, 750, 500, 500, 400, 400, 330, 220, 150, 110, 87, 85, 67, 60, 35, 30,
                                         27.5, 24, 20, 19, 18, 15.75, 15, 13.8, 11, 10.5, 10, 6.6, 6.3, 6, 3.15, 3, 1,
                                         0.66, 0.4, 0.3, 0],
                         isDC=['false', 'false', 'false', 'true', 'false', 'true', 'false', 'false', 'false', 'false',
                               'false', 'true', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false',
                               'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false',
                               'false', 'false', 'false', 'false', 'false', 'false', 'false']
                         )

base_voltage = pd.DataFrame(data=base_voltage_data)


class BaseEquipment(ABC):
    def __init__(self, xml: XmlReader):
        self.xml = xml
        self.tables_list = []

    def run(self) -> pd.DataFrame:
        """По набору тэгов собирает информацию об оборудовании"""
        # Читаем список тегов из xml
        table_dict = self.xml.get_data_by_list(self.tables_list)

        # Объединяем все таблицы
        full_df = self.join_table(table_dict)

        return full_df

    @staticmethod
    def check_structure_xml(df: pd.DataFrame, columns_list: list[str]) -> pd.DataFrame:
        """Проверяет, что все нужные тэги есть в xml.
        Если тэга нет, то заполняет его заглушкой"""

        # Проверка, что все нужные тэги есть в xml
        for column in columns_list:
            if column not in df.columns:
                df[column] = 'ОШИБКА структуры xml. Отсутствует аттрибут или связь.'

        return df

    @abstractmethod
    def join_table(self, table_dict: dict[str: pd.DataFrame]) -> pd.DataFrame:
        pass

    @abstractmethod
    def save_table(self, df: pd.DataFrame, f_name: str):
        pass


class Breaker(BaseEquipment):

    def __init__(self, xml: XmlReader):
        super().__init__(xml)
        self.tables_list = ['Breaker', 'BreakerInfo', 'Asset', 'OperationalLimitSet', 'CurrentLimit', 'VoltageLimit',
                            'Bay', 'VoltageLevel', 'Substation', 'Manufacturer', 'Organisation', 'ProductAssetModel',
                            'Terminal'
                            # , 'ConnectivityNode'
                           ]

    def join_table(self, table_dict: dict[str: pd.DataFrame]) -> pd.DataFrame:
        # Разбор df с проверкой структуры
        breaker = self.check_structure_xml(table_dict.get('Breaker'), ib.breaker_columns)
        breaker_info = self.check_structure_xml(table_dict.get('BreakerInfo'), ib.breaker_info_columns)
        asset = self.check_structure_xml(table_dict.get('Asset'), ib.asset_columns)
        operational_limit_set = self.check_structure_xml(table_dict.get('OperationalLimitSet'),
                                                         ib.operational_limit_set_columns)

        current_limit = table_dict.get('CurrentLimit')
        voltage_limit = table_dict.get('VoltageLimit')

        bay = self.check_structure_xml(table_dict.get('Bay'), ib.bay_columns)
        voltage_level = self.check_structure_xml(table_dict.get('VoltageLevel'), ib.voltage_level_columns)
        substation = self.check_structure_xml(table_dict.get('Substation'), ib.substation_columns)
        manufacturer = self.check_structure_xml(table_dict.get('Manufacturer'), ib.manufacturer_columns)
        organisation = self.check_structure_xml(table_dict.get('Organisation'), ib.organisation_columns)
        product_asset_model = self.check_structure_xml(table_dict.get('ProductAssetModel'), ib.product_asset_model_columns)
        terminal = self.check_structure_xml(table_dict.get('Terminal'), ib.terminal_columns)
        # connectivity_node = self.check_structure_xml(table_dict.get('ConnectivityNode'), connectivity_node_columns)

        # Ошибка структуры xml !!!11
        # try:
        out_df = (breaker
                  .merge(bay[ib.bay_columns],
                         left_on='Equipment.EquipmentContainer', right_on='bay_mRID',
                         how='left', suffixes=('_br', '_bay'))
                  .merge(voltage_level[ib.voltage_level_columns],
                         left_on='Bay.VoltageLevel', right_on='voltagelevel_mRID',
                         how='left', suffixes=('_bay', '_voltlev'))
                  .merge(substation[ib.substation_columns],
                         left_on='VoltageLevel.Substation', right_on='substation_mRID',
                         how='left', suffixes=('_voltlev', '_subst'))
                  .merge(base_voltage[base_voltage_data.keys()],
                         left_on='VoltageLevel.BaseVoltage', right_on='mRID',
                         how='left', suffixes=('_subst', '_base_v'))
                  )
        # except KeyError as e:
        #     m = re.search("'([^']*)'", e.args[0])
        #     key = m.group(1)
        #     print(key)

        out_df = (out_df
                  .merge(asset[ib.asset_columns],
                         left_on='PowerSystemResource.Assets', right_on='asset_mRID',
                         how='left', suffixes=('_base_v', '_asset'))
                  )

        return out_df

    def save_table(self, df: pd.DataFrame, f_name: str):
        dfc = df.copy()

        dfc['Дата получения'] = pd.Timestamp.today()
        dfc['Дата ответа'] = pd.Timestamp.today() + pd.DateOffset(days=10)

        rename_columns = {
            'IdentifiedObject.name_br': 'Наименование выключателя',
            'IdentifiedObject.name_bay': 'Наименование цепи',
        }

        # Нет Данных

        dfc_renamed = dfc.rename(columns=rename_columns)

        file_name = f_name.rsplit("\\", 1)[1].rsplit(".", 1)[0]
        file_date = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
        excel_name = f'{file_name}_Breakers_{file_date}.xlsx'

        with pd.ExcelWriter(excel_name) as writer:
            dfc_renamed.to_excel(writer, sheet_name='Лист1', index=False, )
