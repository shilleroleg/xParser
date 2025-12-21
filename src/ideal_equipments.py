import pandas as pd
import numpy as np


class BaseTag:
    def __init__(self, df: pd.DataFrame):
        self.data = df
        self.columns = []
        self.mRID = None

    def check_structure(self) -> None:
        """Проверяет, что все нужные колонки есть в df.
        Если колонки нет, то добавляем пустой столбец."""

        df = self.data.copy()

        # Проверка, что все нужные тэги есть в xml
        for column in self.columns:
            if column not in df.columns:
                df[column] = 'EMPTY'

        # Задаем количество и порядок колонок как в списке
        self.data = df[self.columns]

        if self.data.empty:
            self.data = pd.concat([self.data, pd.DataFrame([[np.nan] * self.data.shape[1]], columns=self.data.columns)],
                                  ignore_index=True)

        self.data.fillna(value='EMPTY', inplace=True)


class BaseVoltageTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['basevoltage_mRID', 'name', 'nominalVoltage', 'isDC']
        self.mRID = self.columns[0]


class OperationalLimitTypeTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['operationallimittype_mRID', 'IdentifiedObject.name', 'OperationalLimitType.acceptableDuration']
        self.mRID = self.columns[0]

        self.check_structure()


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
        self.mRID = self.columns[0]

        self.check_structure()


# Group 1
class BayTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['bay_mRID', 'IdentifiedObject.name', 'Bay.VoltageLevel']
        self.mRID = self.columns[0]

        self.check_structure()


class VoltageLevelTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['voltagelevel_mRID', 'VoltageLevel.BaseVoltage', 'IdentifiedObject.name',
                        'VoltageLevel.Substation']
        self.mRID = self.columns[0]

        self.check_structure()


class SubstationTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['substation_mRID', 'IdentifiedObject.name', 'Substation.Region']
        self.mRID = self.columns[0]

        self.check_structure()


# Group 2
class AssetTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['asset_mRID', 'IdentifiedObject.name', 'Asset.ProductAssetModel', 'Asset.inUseDate',
                        'Asset.AssetInfo']
        self.mRID = self.columns[0]

        self.check_structure()


class ProductAssetModelTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['productassetmodel_mRID', 'IdentifiedObject.name', 'ProductAssetModel.Manufacturer']
        self.mRID = self.columns[0]

        self.check_structure()


class ManufacturerTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['manufacturer_mRID', 'IdentifiedObject.name', 'OrganisationRole.Organisation']
        self.mRID = self.columns[0]

        self.check_structure()


class OrganisationTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['organisation_mRID', 'IdentifiedObject.name']
        self.mRID = self.columns[0]

        self.check_structure()


class BreakerInfoTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['breakerinfo_mRID', 'IdentifiedObject.name', 'SwitchInfo.ratedVoltage',
                        'SwitchInfo.ratedCurrent', 'SwitchInfo.breakingCapacity', 'BreakerInfo.interruptingTime',
                        'BreakerInfo.ratedRecloseTime', 'SwitchInfo.ratedInterruptingTime',
                        'SwitchInfo.ratedInTransitTime', 'SwitchInfo.isSinglePhase', 'SwitchInfo.isUnganged']
        self.mRID = self.columns[0]

        self.check_structure()


# Group 3
class TerminalTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['terminal_mRID', 'ACDCTerminal.sequenceNumber', 'IdentifiedObject.name',
                        'Terminal.ConductingEquipment', 'Terminal.ConnectivityNode']
        self.mRID = self.columns[0]

        self.check_structure()


# Group 4
class OperationalLimitSetTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['operationallimitset_mRID', 'IdentifiedObject.name', 'OperationalLimitSet.Terminal',
                        'OperationalLimitSet.Equipment']
        self.mRID = self.columns[0]

        self.check_structure()


class VoltageLimitTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['voltagelimit_mRID', 'OperationalLimit.OperationalLimitSet', 'IdentifiedObject.name',
                        'VoltageLimit.value', 'OperationalLimit.OperationalLimitType']
        self.mRID = self.columns[0]

        self.check_structure()


class CurrentLimitTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['currentlimit_mRID', 'OperationalLimit.OperationalLimitSet', 'IdentifiedObject.name',
                        'CurrentLimit.value', 'OperationalLimit.OperationalLimitType',
                        'OperationalLimit.LimitDependencyModel']
        self.mRID = self.columns[0]

        self.check_structure()


class TemperatureDependentLimitTableTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['temperaturedependentlimittable_mRID', 'IdentifiedObject.name']
        self.mRID = self.columns[0]

        self.check_structure()


class TemperatureDependentLimitPointTag(BaseTag):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.columns = ['temperaturedependentlimitpoint_mRID', 'TemperatureDependentLimitPoint.temperature',
                        'TemperatureDependentLimitPoint.limitPercent',
                        'TemperatureDependentLimitPoint.TemperatureDependentLimitTable']
        self.mRID = self.columns[0]

        self.check_structure()
        self.reformat_table()

    def reformat_table(self):
        self.data['TemperatureDependentLimitPoint.temperature'] = \
            self.data['TemperatureDependentLimitPoint.temperature'].replace({'EMPTY': 0})

        self.data['TemperatureDependentLimitPoint.temperature'] = \
            self.data['TemperatureDependentLimitPoint.temperature'].astype(float)

        result = self.data.pivot_table(index='TemperatureDependentLimitPoint.TemperatureDependentLimitTable',
                                       columns='TemperatureDependentLimitPoint.temperature',
                                       values='TemperatureDependentLimitPoint.limitPercent',
                                       aggfunc='first').reset_index()
        result.columns.name = None
        result.columns = [str(col) for col in result.columns]

        self.columns = result.columns
        self.data = result
        self.mRID = 'TemperatureDependentLimitPoint.TemperatureDependentLimitTable'
