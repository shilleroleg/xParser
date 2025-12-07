import re
from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd
import numpy as np

from xml_reader import XmlReader
from ideal_equipments import *
from tools.logger import log


class BaseEquipment(ABC):
    def __init__(self, xml: XmlReader):
        self.mRID = None
        self.xml = xml
        self.tables_list = []
        self.appendix_1 = pd.DataFrame()
        self.appendix_2_1 = pd.DataFrame()
        self.appendix_2_2 = pd.DataFrame()

    def run(self) -> pd.DataFrame:
        """По набору тэгов собирает информацию об оборудовании"""
        # Читаем список тегов из xml
        table_dict = self.xml.get_data_by_list(self.tables_list)

        # Объединяем все таблицы
        self.appendix_1 = self.create_appendix(table_dict)

        return self.appendix_1

    @staticmethod
    def _join(left: pd.DataFrame, right: pd.DataFrame,
              left_on: str, right_on: str,
              suffixes: tuple[str, str] = ('_left', '_right')) -> pd.DataFrame:

        try:
            out_df = (left
                      .merge(right, left_on=left_on, right_on=right_on, how='left', suffixes=suffixes)
                      )
        except ValueError:
            log.warning(f'Правая таблица не содержит запией или пустой ключ {right_on}')
            out_df = left.copy()
        except Exception as e:
            log.error(f'Ошибка при объединении двух таблиц {e}')
            out_df = left.copy()

        return out_df

    @abstractmethod
    def create_appendix(self, table_dict: dict[str: pd.DataFrame]) -> pd.DataFrame:
        pass

    @abstractmethod
    def save_table(self, f_name: str):
        pass


class Breaker(BaseEquipment):

    def __init__(self, xml: XmlReader):
        super().__init__(xml)
        self.mRID = 'breaker_mRID'
        self.tables_list = ['Breaker', 'BreakerInfo', 'Asset', 'OperationalLimitSet', 'CurrentLimit', 'VoltageLimit',
                            'Bay', 'VoltageLevel', 'Substation', 'Manufacturer', 'Organisation', 'ProductAssetModel',
                            'Terminal', 'TemperatureDependentLimitTable', 'TemperatureDependentLimitPoint'
                            # , 'ConnectivityNode'
                            ]

    def create_appendix(self, table_dict: dict[str: pd.DataFrame]) -> pd.DataFrame:
        # Разбор df
        base_voltage = BaseVoltageTag(base_voltage_df)

        breaker = BreakerTag(table_dict.get('Breaker'))
        breaker_info = BreakerInfoTag(table_dict.get('BreakerInfo'))
        asset = AssetTag(table_dict.get('Asset'))
        operational_limit_set = OperationalLimitSetTag(table_dict.get('OperationalLimitSet'))

        current_limit = CurrentLimitTag(table_dict.get('CurrentLimit'))
        voltage_limit = VoltageLimitTag(table_dict.get('VoltageLimit'))

        bay = BayTag(table_dict.get('Bay'))
        voltage_level = VoltageLevelTag(table_dict.get('VoltageLevel'))
        substation = SubstationTag(table_dict.get('Substation'))
        manufacturer = ManufacturerTag(table_dict.get('Manufacturer'))
        organisation = OrganisationTag(table_dict.get('Organisation'))
        product_asset_model = ProductAssetModelTag(table_dict.get('ProductAssetModel'))
        terminal = TerminalTag(table_dict.get('Terminal'))

        temperature_dependent_limit_table = TemperatureDependentLimitTableTag(
            table_dict.get('TemperatureDependentLimitTable'))

        temperature_dependent_limit_point = TemperatureDependentLimitPointTag(
            table_dict.get('TemperatureDependentLimitPoint'))

        # temperature_dependent_limit_point.body.to_pickle('limit_point.pkl')

        out_df = self._join(breaker.body, bay.body,
                            left_on='Equipment.EquipmentContainer', right_on=bay.mRID, suffixes=('_br', '_bay'))
        out_df = self._join(out_df, voltage_level.body,
                            left_on='Bay.VoltageLevel', right_on=voltage_level.mRID, suffixes=('_bay', '_voltlev'))
        out_df = self._join(out_df, substation.body,
                            left_on='VoltageLevel.Substation', right_on=substation.mRID,
                            suffixes=('_voltlev', '_subst'))
        out_df = self._join(out_df, base_voltage.body,
                            left_on='VoltageLevel.BaseVoltage', right_on=base_voltage.mRID,
                            suffixes=('_subst', '_base_v'))

        out_df = self._join(out_df, asset.body,
                            left_on='PowerSystemResource.Assets', right_on=asset.mRID,
                            suffixes=('_base_v', '_asset'))
        out_df = self._join(out_df, product_asset_model.body,
                            left_on='Asset.ProductAssetModel', right_on=product_asset_model.mRID,
                            suffixes=('_asset', '_pam'))
        out_df = self._join(out_df, manufacturer.body,
                            left_on='ProductAssetModel.Manufacturer', right_on=manufacturer.mRID,
                            suffixes=('_pam', '_manufact'))
        out_df = self._join(out_df, organisation.body,
                            left_on='OrganisationRole.Organisation', right_on=organisation.mRID,
                            suffixes=('_manufact', '_org'))

        # Может быть заполнен или AssetDatasheet или AssetInfo
        if (asset.body['Asset.AssetInfo'].isnull() | asset.body['Asset.AssetInfo'].astype(str).str.strip().eq('')) \
                .all():
            out_df = self._join(out_df, breaker_info.body,
                                left_on='PowerSystemResource.AssetDatasheet', right_on=breaker_info.mRID,
                                suffixes=('_br2', '_info'))
        else:
            out_df = self._join(out_df, breaker_info.body,
                                left_on='Asset.AssetInfo', right_on=breaker_info.mRID, suffixes=('_br2', '_info'))

        # Порядок полюсов в файле может быть перепутан - указываем его явно
        terminal_1 = terminal.body[terminal.body['ACDCTerminal.sequenceNumber'] == '1']
        terminal_2 = terminal.body[terminal.body['ACDCTerminal.sequenceNumber'] == '2']

        out_df = self._join(out_df, terminal_1,
                            left_on=breaker.mRID, right_on='Terminal.ConductingEquipment', suffixes=('_br3', '_T1'))
        out_df = self._join(out_df, terminal_2,
                            left_on=breaker.mRID, right_on='Terminal.ConductingEquipment', suffixes=('_br4', '_T2'))

        # Собираем вторую фактуру
        out_df_2_1 = (current_limit.body
                      .merge(operational_limit_set.body,
                             left_on='OperationalLimit.OperationalLimitSet', right_on=operational_limit_set.mRID,
                             how='left', suffixes=('_curlimit', '_OLSetI'))
                      .merge(breaker.body[['breaker_mRID', 'IdentifiedObject.name']],
                             left_on='OperationalLimitSet.Equipment', right_on=breaker.mRID,
                             how='left', suffixes=('_OLSetI', '_br'))
                      .merge(temperature_dependent_limit_table.body,
                             left_on='OperationalLimit.LimitDependencyModel',
                             right_on=temperature_dependent_limit_table.mRID,
                             how='left', suffixes=('_curlimit2', '_Table'))
                      .merge(temperature_dependent_limit_point.body,
                             left_on=temperature_dependent_limit_table.mRID,
                             right_on=temperature_dependent_limit_point.mRID,
                             how='left', suffixes=('_Table', '_Point'))
                      )
        out_df_2_1.dropna(axis=0, subset=[breaker.mRID], inplace=True)

        # Собираем третью фактуру
        out_df_2_2 = (voltage_limit.body
                      .merge(operational_limit_set.body,
                             left_on='OperationalLimit.OperationalLimitSet', right_on=operational_limit_set.mRID,
                             how='left', suffixes=('_voltlimit', '_OLSetV'))
                      .merge(breaker.body[['breaker_mRID', 'IdentifiedObject.name']],
                             left_on='OperationalLimitSet.Equipment', right_on=breaker.mRID,
                             how='left', suffixes=('_OLSetV', '_br'))
                      )
        out_df_2_2.dropna(axis=0, subset=[breaker.mRID], inplace=True)

        self.appendix_1 = out_df.copy()
        self.appendix_2_1 = out_df_2_1.copy()
        self.appendix_2_2 = out_df_2_2.copy()

        return out_df

    def save_table(self, f_name: str):
        dfc1 = self.appendix_1.copy()
        dfc2_1 = self.appendix_2_1.copy()
        dfc2_2 = self.appendix_2_2.copy()

        dfc1['Дата получения'] = pd.Timestamp.today()
        dfc1['Дата ответа'] = pd.Timestamp.today() + pd.DateOffset(days=10)

        # rename_columns = {
        #     'IdentifiedObject.name_br': 'Наименование выключателя',
        #     'IdentifiedObject.name_bay': 'Наименование цепи',
        # }
        # dfc_renamed = dfc1.rename(columns=rename_columns)

        file_name = f_name.rsplit("\\", 1)[1].rsplit(".", 1)[0]
        file_date = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
        excel_name = f'xlsx\\{file_name}_Breakers_{file_date}.xlsx'

        with pd.ExcelWriter(excel_name) as writer:
            dfc1.to_excel(writer, sheet_name='Лист1', index=False, )
            dfc2_1.to_excel(writer, sheet_name='current_limit', index=False, )
            dfc2_2.to_excel(writer, sheet_name='voltage_limit', index=False, )
