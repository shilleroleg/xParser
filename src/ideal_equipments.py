# from dataclasses import dataclass
import pandas as pd
import numpy as np

base_voltage_data = dict(
    basevoltage_mRID=['10000643-0000-0000-c000-0000006d746c', '1000068b-0000-0000-c000-0000006d746c',
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

base_voltage_df = pd.DataFrame(data=base_voltage_data)


# @dataclass
# class IdealBreaker:
#     breaker_columns: list[str]
#     breaker_info_columns: list[str]
#     asset_columns: list[str]
#     operational_limit_set_columns: list[str]
#     current_limit_columns: list[str]
#     voltage_limit_columns: list[str]
#     bay_columns: list[str]
#     voltage_level_columns: list[str]
#     substation_columns: list[str]
#     manufacturer_columns: list[str]
#     organisation_columns: list[str]
#     product_asset_model_columns: list[str]
#     terminal_columns: list[str]
#     # temperature_dependent_limit_table_columns: list[str]
#     # temperature_dependent_limit_point_columns: list[str]
#     # решили не нужно, достаточно сравнивать уид в свойстве полюса (терминала)
#     # connectivity_node_columns: list[str]
#
#
# ideal_breaker = IdealBreaker(
#     breaker_columns=['breaker_mRID', 'IdentifiedObject.name', 'Equipment.EquipmentContainer',
#                      'PowerSystemResource.Assets', 'PowerSystemResource.AssetDatasheet',
#                      'ConductingEquipment.Terminals', 'ConductingEquipment.Terminals_2',
#                      'ConductingEquipment.BaseVoltage', 'Equipment.normallyInService',
#                      'ConductingEquipment.isThreePhaseEquipment',
#                      'Switch.ratedCurrent', 'ProtectedSwitch.breakingCapacity',
#                      'Switch.normalOpen', 'Breaker.inTransitTime', 'Switch.differenceInTransitTime',
#                      'Equipment.OperationalLimitSet', 'Equipment.OperationalLimitSet_2'],
#     # Группа 1
#     bay_columns=['bay_mRID', 'IdentifiedObject.name', 'Bay.VoltageLevel'],
#     voltage_level_columns=['voltagelevel_mRID', 'VoltageLevel.BaseVoltage', 'IdentifiedObject.name',
#                            'VoltageLevel.Substation'],
#     substation_columns=['substation_mRID', 'IdentifiedObject.name', 'Substation.Region'],
#     # Группа 2
#     asset_columns=['asset_mRID', 'IdentifiedObject.name', 'Asset.ProductAssetModel', 'Asset.inUseDate',
#                    'Asset.AssetInfo'],
#     product_asset_model_columns=['productassetmodel_mRID', 'IdentifiedObject.name', 'ProductAssetModel.Manufacturer'],
#     manufacturer_columns=['manufacturer_mRID', 'IdentifiedObject.name', 'OrganisationRole.Organisation'],
#     organisation_columns=['organisation_mRID', 'IdentifiedObject.name'],
#     breaker_info_columns=['breakerinfo_mRID', 'IdentifiedObject.name', 'SwitchInfo.ratedVoltage',
#                           'SwitchInfo.ratedCurrent',
#                           'SwitchInfo.breakingCapacity', 'BreakerInfo.interruptingTime', 'BreakerInfo.ratedRecloseTime',
#                           'SwitchInfo.ratedInterruptingTime', 'SwitchInfo.ratedInTransitTime',
#                           'SwitchInfo.isSinglePhase', 'SwitchInfo.isUnganged'],
#     # Группа 3
#     terminal_columns=['terminal_mRID', 'ACDCTerminal.sequenceNumber', 'IdentifiedObject.name',
#                       'Terminal.ConductingEquipment', 'Terminal.ConnectivityNode', 'ACDCTerminal.OperationalLimitSet'],
#     # Группа 4
#     operational_limit_set_columns=['operationallimitset_mRID', 'IdentifiedObject.name',
#                                    'OperationalLimitSet.Terminal', 'OperationalLimitSet.Equipment'],
#     voltage_limit_columns=['voltagelimit_mRID', 'OperationalLimit.OperationalLimitSet', 'IdentifiedObject.name',
#                            'VoltageLimit.value', 'OperationalLimit.OperationalLimitType'],
#     current_limit_columns=['currentlimit_mRID', 'OperationalLimit.OperationalLimitSet', 'IdentifiedObject.name',
#                            'CurrentLimit.value', 'OperationalLimit.OperationalLimitType',
#                            'OperationalLimit.LimitDependencyModel'],
# )


class BaseTag:
    def __init__(self, df: pd.DataFrame):
        self.body = df
        self.columns = []

    def check_structure(self) -> None:
        """Проверяет, что все нужные колонки есть в df.
        Если колонки нет, то добавляем пустой столбец."""

        df = self.body.copy()

        # Проверка, что все нужные тэги есть в xml
        for column in self.columns:
            if column not in df.columns:
                df[column] = np.nan

        # Задаем количество и порядок колонок как в списке
        self.body = df[self.columns]


class BaseVoltageTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['basevoltage_mRID', 'name', 'nominalVoltage', 'isDC']


class BreakerTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['breaker_mRID', 'IdentifiedObject.name', 'Equipment.EquipmentContainer',
                        'PowerSystemResource.Assets', 'PowerSystemResource.AssetDatasheet',
                        'ConductingEquipment.BaseVoltage', 'Equipment.normallyInService',
                        'ConductingEquipment.isThreePhaseEquipment',
                        'Switch.ratedCurrent', 'ProtectedSwitch.breakingCapacity',
                        'Switch.normalOpen', 'Breaker.inTransitTime', 'Switch.differenceInTransitTime',
                        ]

        self.check_structure()


# Group 1
class BayTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['bay_mRID', 'IdentifiedObject.name', 'Bay.VoltageLevel']

        self.check_structure()


class VoltageLevelTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['voltagelevel_mRID', 'VoltageLevel.BaseVoltage', 'IdentifiedObject.name',
                        'VoltageLevel.Substation']

        self.check_structure()


class SubstationTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['substation_mRID', 'IdentifiedObject.name', 'Substation.Region']

        self.check_structure()


# Group 2
class AssetTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['asset_mRID', 'IdentifiedObject.name', 'Asset.ProductAssetModel', 'Asset.inUseDate',
                        'Asset.AssetInfo']

        self.check_structure()


class ProductAssetModelTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['productassetmodel_mRID', 'IdentifiedObject.name', 'ProductAssetModel.Manufacturer']

        self.check_structure()


class ManufacturerTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['manufacturer_mRID', 'IdentifiedObject.name', 'OrganisationRole.Organisation']

        self.check_structure()


class OrganisationTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['organisation_mRID', 'IdentifiedObject.name']

        self.check_structure()


class BreakerInfoTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['breakerinfo_mRID', 'IdentifiedObject.name', 'SwitchInfo.ratedVoltage',
                        'SwitchInfo.ratedCurrent', 'SwitchInfo.breakingCapacity', 'BreakerInfo.interruptingTime',
                        'BreakerInfo.ratedRecloseTime', 'SwitchInfo.ratedInterruptingTime',
                        'SwitchInfo.ratedInTransitTime', 'SwitchInfo.isSinglePhase', 'SwitchInfo.isUnganged']

        self.check_structure()


# Group 3
class TerminalTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['terminal_mRID', 'ACDCTerminal.sequenceNumber', 'IdentifiedObject.name',
                        'Terminal.ConductingEquipment', 'Terminal.ConnectivityNode']

        self.check_structure()


# Group 4
class OperationalLimitSetTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['operationallimitset_mRID', 'IdentifiedObject.name', 'OperationalLimitSet.Terminal',
                        'OperationalLimitSet.Equipment']

        self.check_structure()


class VoltageLimitTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['voltagelimit_mRID', 'OperationalLimit.OperationalLimitSet', 'IdentifiedObject.name',
                        'VoltageLimit.value', 'OperationalLimit.OperationalLimitType']

        self.check_structure()


class CurrentLimitTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['currentlimit_mRID', 'OperationalLimit.OperationalLimitSet', 'IdentifiedObject.name',
                        'CurrentLimit.value', 'OperationalLimit.OperationalLimitType',
                        'OperationalLimit.LimitDependencyModel']

        self.check_structure()
