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
        self.xml = xml
        self.tables_list = []
        self.final_table = pd.DataFrame()

    def run(self) -> pd.DataFrame:
        """По набору тэгов собирает информацию об оборудовании"""
        # Читаем список тегов из xml
        table_dict = self.xml.get_data_by_list(self.tables_list)

        # Объединяем все таблицы
        self.final_table = self.join_table(table_dict)

        return self.final_table

    # @staticmethod
    # def check_structure_xml(df: pd.DataFrame, columns_list: list[str]) -> pd.DataFrame:
    #     """Проверяет, что все нужные тэги есть в xml.
    #     Если тэга нет, то заполняет его заглушкой"""
    #
    #     # Проверка, что все нужные тэги есть в xml
    #     for column in columns_list:
    #         if column not in df.columns:
    #             df[column] = np.nan
    #
    #     return df

    @abstractmethod
    def join_table(self, table_dict: dict[str: pd.DataFrame]) -> pd.DataFrame:
        pass

    @abstractmethod
    def save_table(self, f_name: str):
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

        # breaker = self.check_structure_xml(table_dict.get('Breaker'), ib.breaker_columns)
        # breaker_info = self.check_structure_xml(table_dict.get('BreakerInfo'), ib.breaker_info_columns)
        # asset = self.check_structure_xml(table_dict.get('Asset'), ib.asset_columns)
        # operational_limit_set = self.check_structure_xml(table_dict.get('OperationalLimitSet'),
        #                                                  ib.operational_limit_set_columns)
        # #
        # # current_limit = table_dict.get('CurrentLimit')
        # voltage_limit = self.check_structure_xml(table_dict.get('VoltageLimit'), ib.voltage_limit_columns)
        #
        # bay = self.check_structure_xml(table_dict.get('Bay'), ib.bay_columns)
        # voltage_level = self.check_structure_xml(table_dict.get('VoltageLevel'), ib.voltage_level_columns)
        # substation = self.check_structure_xml(table_dict.get('Substation'), ib.substation_columns)
        # manufacturer = self.check_structure_xml(table_dict.get('Manufacturer'), ib.manufacturer_columns)
        # organisation = self.check_structure_xml(table_dict.get('Organisation'), ib.organisation_columns)
        # product_asset_model = self.check_structure_xml(table_dict.get('ProductAssetModel'), ib.product_asset_model_columns)
        # terminal = self.check_structure_xml(table_dict.get('Terminal'), ib.terminal_columns)
        # connectivity_node = self.check_structure_xml(table_dict.get('ConnectivityNode'), connectivity_node_columns)

        out_df = (breaker.body
                  .merge(bay.body,
                         left_on='Equipment.EquipmentContainer', right_on='bay_mRID',
                         how='left', suffixes=('_br', '_bay'))
                  .merge(voltage_level.body,
                         left_on='Bay.VoltageLevel', right_on='voltagelevel_mRID',
                         how='left', suffixes=('_bay', '_voltlev'))
                  .merge(substation.body,
                         left_on='VoltageLevel.Substation', right_on='substation_mRID',
                         how='left', suffixes=('_voltlev', '_subst'))
                  .merge(base_voltage.body,
                         left_on='VoltageLevel.BaseVoltage', right_on='basevoltage_mRID',
                         how='left', suffixes=('_subst', '_base_v'))
                  )

        out_df = (out_df
                  .merge(asset.body,
                         left_on='PowerSystemResource.Assets', right_on='asset_mRID',
                         how='left', suffixes=('_base_v', '_asset'))
                  .merge(product_asset_model.body,
                         left_on='Asset.ProductAssetModel', right_on='productassetmodel_mRID',
                         how='left', suffixes=('_asset', '_pam'))
                  .merge(manufacturer.body,
                         left_on='ProductAssetModel.Manufacturer', right_on='manufacturer_mRID',
                         how='left', suffixes=('_pam', '_manufact'))
                  .merge(organisation.body,
                         left_on='OrganisationRole.Organisation', right_on='organisation_mRID',
                         how='left', suffixes=('_manufact', '_org'))
                  )

        # Может быть заполнен или AssetDatasheet или AssetInfo
        if (asset.body['Asset.AssetInfo'].isnull() | asset.body['Asset.AssetInfo'].astype(str).str.strip().eq(''))\
                .all():
            out_df = (out_df
                      .merge(breaker_info.body,
                             left_on='PowerSystemResource.AssetDatasheet', right_on='breakerinfo_mRID',
                             how='left', suffixes=('_br2', '_info'))
                      )
        else:
            out_df = (out_df
                      .merge(breaker_info.body,
                             left_on='Asset.AssetInfo', right_on='breakerinfo_mRID',
                             how='left', suffixes=('_br2', '_info'))
                      )
        # Порядок полюсов в файле может быть перепутан - указываем его явно
        terminal_1 = terminal.body[terminal.body['ACDCTerminal.sequenceNumber'] == '1']
        terminal_2 = terminal.body[terminal.body['ACDCTerminal.sequenceNumber'] == '2']

        out_df = (out_df
                  .merge(terminal_1,
                         left_on='breaker_mRID', right_on='Terminal.ConductingEquipment',
                         how='left', suffixes=('_br3', '_T1'))
                  .merge(terminal_2,
                         left_on='breaker_mRID', right_on='Terminal.ConductingEquipment',
                         how='left', suffixes=('_br4', '_T2'))
                  )

        # Собираем вторую фактуру
        out_df_2_2 = (voltage_limit.body
                      .merge(operational_limit_set.body,
                             left_on='OperationalLimit.OperationalLimitSet', right_on='operationallimitset_mRID',
                             how='left', suffixes=('_voltlimit', '_OLSetV'))
                      .merge(breaker.body[['breaker_mRID', 'IdentifiedObject.name']],
                             left_on='OperationalLimitSet.Equipment', right_on='breaker_mRID',
                             how='left', suffixes=('_OLSetV', '_br5'))
                      )

        out_df_2_2.dropna(axis=0, subset=['breaker_mRID'], inplace=True)
        with pd.ExcelWriter('xlsx\\out_df_2_2.xlsx') as writer:
            out_df_2_2.to_excel(writer, sheet_name='Лист1', index=False, )

        return out_df

    def save_table(self, f_name: str):
        dfc = self.final_table.copy()

        dfc['Дата получения'] = pd.Timestamp.today()
        dfc['Дата ответа'] = pd.Timestamp.today() + pd.DateOffset(days=10)

        # rename_columns = {
        #     'IdentifiedObject.name_br': 'Наименование выключателя',
        #     'IdentifiedObject.name_bay': 'Наименование цепи',
        # }
        # dfc_renamed = dfc.rename(columns=rename_columns)

        file_name = f_name.rsplit("\\", 1)[1].rsplit(".", 1)[0]
        file_date = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
        excel_name = f'xlsx\\{file_name}_Breakers_{file_date}.xlsx'

        with pd.ExcelWriter(excel_name) as writer:
            dfc.to_excel(writer, sheet_name='Лист1', index=False, )
