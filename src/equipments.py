from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from comparer import Comparer
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
        self.appendix_2_2_pivot = pd.DataFrame()

        self.compare_1 = pd.DataFrame()
        self.compare_2_1 = pd.DataFrame()

    def run(self) -> pd.DataFrame:
        """По набору тэгов собирает информацию об оборудовании"""
        # Читаем список тегов из xml
        table_dict = self.xml.get_data_by_list(self.tables_list)

        # Объединяем все таблицы
        self.appendix_1 = self.create_appendix(table_dict)

        return self.appendix_1

    @staticmethod
    def _left_join(left: pd.DataFrame,
                   right: pd.DataFrame,
                   left_on: str,
                   right_on: str,
                   suffixes: tuple[str, str] = ('_left', '_right')) -> pd.DataFrame:
        """Метод-обертка для библиотечного метода merge. Нужен для обработки ошибок"""

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
    def save_table(self, f_name: str) -> None:
        pass

    @abstractmethod
    def compare(self, other: BaseEquipment):
        pass


class Breaker(BaseEquipment):

    def __init__(self, xml: XmlReader):
        super().__init__(xml)
        self.mRID = 'breaker_mRID'
        self.tables_list = ['Breaker', 'BreakerInfo', 'Asset', 'OperationalLimitSet', 'CurrentLimit', 'VoltageLimit',
                            'Bay', 'VoltageLevel', 'Substation', 'Manufacturer', 'Organisation', 'ProductAssetModel',
                            'Terminal', 'TemperatureDependentLimitTable', 'TemperatureDependentLimitPoint'
                            ]

    def create_appendix(self, table_dict: dict[str: pd.DataFrame]) -> pd.DataFrame:
        """Основной метод для расчета всех фактур"""

        log.info('Разбор всех датафреймов')

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

        # Словари считываем отдельно из xml
        bv_name = r'dict\base_voltage.xml'
        bv_xml = XmlReader(bv_name)
        bv_df = bv_xml.get_data_by_tag('BaseVoltage')
        base_voltage = BaseVoltageTag(bv_df)

        olt_name = r'dict\operational_limit_type.xml'
        olt_xml = XmlReader(olt_name)
        olt_df = olt_xml.get_data_by_tag('OperationalLimitType')
        operational_limit_type = OperationalLimitTypeTag(olt_df)

        log.info('Собираем первую фактуру')
        out_df = self._left_join(breaker.data, bay.data,
                                 left_on='Equipment.EquipmentContainer', right_on=bay.mRID, suffixes=('_br', '_bay'))
        out_df = self._left_join(out_df, voltage_level.data,
                                 left_on='Bay.VoltageLevel', right_on=voltage_level.mRID, suffixes=('_bay', '_voltlev'))
        out_df = self._left_join(out_df, substation.data,
                                 left_on='VoltageLevel.Substation', right_on=substation.mRID,
                                 suffixes=('_voltlev', '_subst'))
        out_df = self._left_join(out_df, base_voltage.data,
                                 left_on='VoltageLevel.BaseVoltage', right_on=base_voltage.mRID,
                                 suffixes=('_subst', '_base_v'))

        out_df = self._left_join(out_df, asset.data,
                                 left_on='PowerSystemResource.Assets', right_on=asset.mRID,
                                 suffixes=('_base_v', '_asset'))
        out_df = self._left_join(out_df, product_asset_model.data,
                                 left_on='Asset.ProductAssetModel', right_on=product_asset_model.mRID,
                                 suffixes=('_asset', '_pam'))
        out_df = self._left_join(out_df, manufacturer.data,
                                 left_on='ProductAssetModel.Manufacturer', right_on=manufacturer.mRID,
                                 suffixes=('_pam', '_manufact'))
        out_df = self._left_join(out_df, organisation.data,
                                 left_on='OrganisationRole.Organisation', right_on=organisation.mRID,
                                 suffixes=('_manufact', '_org'))

        # Может быть заполнен или AssetDatasheet или AssetInfo
        if (out_df['Asset.AssetInfo'].isnull() | out_df['Asset.AssetInfo'].astype(str).str.strip().eq('')).all():
            out_df = self._left_join(out_df, breaker_info.data,
                                     left_on='PowerSystemResource.AssetDatasheet', right_on=breaker_info.mRID,
                                     suffixes=('_br2', '_info'))
        else:
            out_df = self._left_join(out_df, breaker_info.data,
                                     left_on='Asset.AssetInfo', right_on=breaker_info.mRID, suffixes=('_br2', '_info'))

        # Порядок полюсов в файле может быть перепутан - указываем его явно
        terminal_1 = terminal.data[terminal.data['ACDCTerminal.sequenceNumber'] == '1']
        terminal_2 = terminal.data[terminal.data['ACDCTerminal.sequenceNumber'] == '2']

        out_df = self._left_join(out_df, terminal_1,
                                 left_on=breaker.mRID, right_on='Terminal.ConductingEquipment', suffixes=('_br3', '_T1'))
        out_df = self._left_join(out_df, terminal_2,
                                 left_on=breaker.mRID, right_on='Terminal.ConductingEquipment', suffixes=('_br4', '_T2'))

        log.info('Собираем вторую фактуру по CurrentLimit')
        out_df_2_1 = self._left_join(current_limit.data, operational_limit_type.data,
                                     left_on='OperationalLimit.OperationalLimitType', right_on=operational_limit_type.mRID,
                                     suffixes=('_curlimit', '_olt'))
        out_df_2_1 = self._left_join(out_df_2_1, operational_limit_set.data,
                                     left_on='OperationalLimit.OperationalLimitSet', right_on=operational_limit_set.mRID,
                                     suffixes=('_olt', '_OLSetI'))
        out_df_2_1 = self._left_join(out_df_2_1,
                                     breaker.data[['breaker_mRID', 'IdentifiedObject.name', 'Switch.ratedCurrent']],
                                     left_on='OperationalLimitSet.Equipment', right_on=breaker.mRID,
                                     suffixes=('_OLSetI', '_br'))
        out_df_2_1 = self._left_join(out_df_2_1, temperature_dependent_limit_table.data,
                                     left_on='OperationalLimit.LimitDependencyModel',
                                     right_on=temperature_dependent_limit_table.mRID,
                                     suffixes=('_curlimit2', '_Table'))
        out_df_2_1 = self._left_join(out_df_2_1, temperature_dependent_limit_point.body,
                                     left_on=temperature_dependent_limit_table.mRID,
                                     right_on=temperature_dependent_limit_point.mRID,
                                     suffixes=('_Table', '_Point'))

        out_df_2_1.dropna(axis=0, subset=[breaker.mRID], inplace=True)

        log.info('Собираем третью фактуру по VoltageLimit')
        out_df_2_2 = self._left_join(voltage_limit.data, operational_limit_type.data,
                                     left_on='OperationalLimit.OperationalLimitType', right_on=operational_limit_type.mRID,
                                     suffixes=('_voltlimit', '_olt'))
        out_df_2_2 = self._left_join(out_df_2_2, operational_limit_set.data,
                                     left_on='OperationalLimit.OperationalLimitSet', right_on=operational_limit_set.mRID,
                                     suffixes=('_olt', '_OLSetV'))
        out_df_2_2 = self._left_join(out_df_2_2, breaker.data[['breaker_mRID', 'IdentifiedObject.name']],
                                     left_on='OperationalLimitSet.Equipment', right_on=breaker.mRID,
                                     suffixes=('_OLSetV', '_br'))

        out_df_2_2.dropna(axis=0, subset=[breaker.mRID], inplace=True)

        log.info('Собираем свод по VoltageLimit')
        out_df_2_2['IdentifiedObject.name_olt'] = out_df_2_2['IdentifiedObject.name_olt'].fillna('Unknown')
        out_df_2_2_pivot = out_df_2_2.pivot_table(index=breaker.mRID,
                                                  columns='IdentifiedObject.name_olt',
                                                  values='VoltageLimit.value',
                                                  aggfunc='first').reset_index()

        self.appendix_1 = out_df.copy()
        self.appendix_2_1 = out_df_2_1.copy()
        self.appendix_2_2 = out_df_2_2.copy()
        self.appendix_2_2_pivot = out_df_2_2_pivot.copy()

        return out_df

    def compare(self, other: Breaker):
        comparer_1 = Comparer(self.appendix_1, other.appendix_1, 'breaker_mRID')
        comparer_2_1 = Comparer(self.appendix_2_1, other.appendix_2_1, 'currentlimit_mRID')

        # Проверяем наличие ParentObject. Запустить один раз.
        comparer_1.check_xml(self.xml.xml_txt)

        log.info('Запуск сравнялки для главной фактуры')
        self.compare_1 = comparer_1.run()
        log.info('Запуск сравнялки для фактуры CurrentLimit')
        self.compare_2_1 = comparer_2_1.run()

    def save_table(self, f_name: str):
        """Сохраняем все рассчитанные таблицы в xlsx"""

        # В эксель сохраняем только нужные колонки
        breaker_columns = ['breaker_mRID', 'IdentifiedObject.name_br', 'Equipment.normallyInService',
                           'ConductingEquipment.isThreePhaseEquipment', 'Switch.ratedCurrent',
                           'ProtectedSwitch.breakingCapacity', 'Switch.normalOpen', 'Breaker.inTransitTime',
                           'bay_mRID', 'IdentifiedObject.name_bay', 'voltagelevel_mRID',
                           'IdentifiedObject.name_voltlev', 'substation_mRID', 'IdentifiedObject.name_subst',
                           'asset_mRID', 'Asset.inUseDate', 'Asset.AssetInfo', 'IdentifiedObject.name_pam',
                           'IdentifiedObject.name_org', 'breakerinfo_mRID', 'IdentifiedObject.name_br3',
                           'SwitchInfo.ratedVoltage', 'SwitchInfo.ratedCurrent', 'SwitchInfo.breakingCapacity',
                           'BreakerInfo.interruptingTime', 'BreakerInfo.ratedRecloseTime',
                           'SwitchInfo.ratedInterruptingTime', 'SwitchInfo.ratedInTransitTime',
                           'SwitchInfo.isSinglePhase', 'SwitchInfo.isUnganged', 'terminal_mRID_br4',
                           'ACDCTerminal.sequenceNumber_br4', 'Terminal.ConnectivityNode_br4', 'terminal_mRID_T2',
                           'ACDCTerminal.sequenceNumber_T2', 'Terminal.ConnectivityNode_T2']
        current_limit_columns = ['currentlimit_mRID', 'IdentifiedObject.name_curlimit', 'CurrentLimit.value',
                                 'OperationalLimit.LimitDependencyModel', 'operationallimittype_mRID',
                                 'IdentifiedObject.name_olt', 'OperationalLimitType.acceptableDuration',
                                 'operationallimitset_mRID', 'IdentifiedObject.name_OLSetI',
                                 'OperationalLimitSet.Terminal', 'breaker_mRID', 'IdentifiedObject.name_br',
                                 'Switch.ratedCurrent', 'temperaturedependentlimittable_mRID', 'IdentifiedObject.name',
                                 'TemperatureDependentLimitPoint.TemperatureDependentLimitTable']
        voltage_limit_columns = ['voltagelimit_mRID', 'IdentifiedObject.name_voltlimit', 'VoltageLimit.value',
                                 'operationallimittype_mRID', 'IdentifiedObject.name_olt',
                                 'OperationalLimitType.acceptableDuration', 'operationallimitset_mRID',
                                 'IdentifiedObject.name_OLSetV', 'OperationalLimitSet.Terminal', 'breaker_mRID',
                                 'IdentifiedObject.name_br']

        dfc1 = self.compare_1[breaker_columns].copy()
        dfc2_1 = self.compare_2_1[current_limit_columns].copy()
        dfc2_2 = self.appendix_2_2[voltage_limit_columns].copy()
        dfc2_2_pivot = self.appendix_2_2_pivot.copy()

        dfc1['Дата получения'] = pd.Timestamp.today()
        dfc1['Дата ответа'] = pd.Timestamp.today() + pd.DateOffset(days=10)

        # rename_columns = {
        #     'IdentifiedObject.name_br': 'Наименование выключателя',
        #     'IdentifiedObject.name_bay': 'Наименование цепи',
        # }
        # dfc_renamed = dfc1.rename(columns=rename_columns)

        file_name = f_name.rsplit("\\", 1)[1].rsplit(".", 1)[0]
        file_date = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
        excel_name_long = f'xlsx\\{file_name}_Breakers_long_{file_date}.xlsx'
        excel_name_short = f'xlsx\\{file_name}_Breakers_short_{file_date}.xlsx'

        log.info('Сохраняем полную версию фактуры')
        with pd.ExcelWriter(excel_name_long) as writer:
            dfc1.to_excel(writer, sheet_name='breaker', index=False, )
            dfc2_1.to_excel(writer, sheet_name='current_limit', index=False, )
            dfc2_2.to_excel(writer, sheet_name='voltage_limit_full', index=False, )

        log.info('Сохраняем краткую версию фактуры')
        breaker_columns_short = ['IdentifiedObject.name_br', 'Equipment.normallyInService',
                                 'ConductingEquipment.isThreePhaseEquipment', 'Switch.ratedCurrent',
                                 'ProtectedSwitch.breakingCapacity', 'Switch.normalOpen', 'Breaker.inTransitTime',
                                 'IdentifiedObject.name_bay', 'IdentifiedObject.name_voltlev',
                                 'IdentifiedObject.name_subst',
                                 'Asset.inUseDate', 'Asset.AssetInfo', 'IdentifiedObject.name_pam',
                                 'IdentifiedObject.name_org', 'IdentifiedObject.name_br3',
                                 'SwitchInfo.ratedVoltage', 'SwitchInfo.ratedCurrent', 'SwitchInfo.breakingCapacity',
                                 'BreakerInfo.interruptingTime', 'BreakerInfo.ratedRecloseTime',
                                 'SwitchInfo.ratedInterruptingTime', 'SwitchInfo.ratedInTransitTime',
                                 'SwitchInfo.isSinglePhase', 'SwitchInfo.isUnganged',
                                 'ACDCTerminal.sequenceNumber_br4', 'ACDCTerminal.sequenceNumber_T2']

        with pd.ExcelWriter(excel_name_short) as writer:
            dfc1[breaker_columns_short].to_excel(writer, sheet_name='breaker', index=False, )
            dfc2_1.to_excel(writer, sheet_name='current_limit', index=False, )
            dfc2_2_pivot.to_excel(writer, sheet_name='voltage_limit', index=False, )


class PowerTransformer(BaseEquipment):

    def __init__(self, xml: XmlReader):
        super().__init__(xml)
        self.mRID = ''
        self.tables_list = []

    def create_appendix(self, table_dict: dict[str: pd.DataFrame]) -> pd.DataFrame:
        pass

    def compare(self, other: PowerTransformer):
        pass

    def save_table(self, f_name: str) -> None:
        pass