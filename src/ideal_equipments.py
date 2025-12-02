from dataclasses import dataclass


@dataclass
class IdealBreaker:
    breaker_columns: list[str]
    breaker_info_columns: list[str]
    asset_columns: list[str]
    operational_limit_set_columns: list[str]
    current_limit_columns: list[str]
    voltage_limit_columns: list[str]
    bay_columns: list[str]
    voltage_level_columns: list[str]
    substation_columns: list[str]
    manufacturer_columns: list[str]
    organisation_columns: list[str]
    product_asset_model_columns: list[str]
    terminal_columns: list[str]
    temperature_dependent_limit_table_columns: list[str]
    temperature_dependent_limit_point_columns: list[str]
    # решили не нужно, достаточно сравнивать уид в свойстве полюса (терминала)
    # connectivity_node_columns: list[str]


ideal_breaker = IdealBreaker(
    breaker_columns=['breaker_mRID', 'Equipment.normallyInService', 'Equipment.EquipmentContainer',
                     'Equipment.OperationalLimitSet', 'Equipment.OperationalLimitSet_2',
                     'PowerSystemResource.Assets', 'PowerSystemResource.AssetDatasheet',
                     'IdentifiedObject.name', 'ConductingEquipment.Terminals',
                     'ConductingEquipment.Terminals_2', 'ConductingEquipment.BaseVoltage',
                     'ConductingEquipment.isThreePhaseEquipment', 'ProtectedSwitch.breakingCapacity',
                     'Switch.normalOpen', 'Switch.ratedCurrent', 'Breaker.inTransitTime',
                     'Switch.differenceInTransitTime'],
    breaker_info_columns=['breakerinfo_mRID', 'IdentifiedObject.name', 'SwitchInfo.ratedVoltage',
                          'SwitchInfo.ratedCurrent', 'SwitchInfo.breakingCapacity',
                          'BreakerInfo.interruptingTime', 'BreakerInfo.ratedRecloseTime',
                          'SwitchInfo.ratedInterruptingTime', 'SwitchInfo.ratedInTransitTime',
                          'SwitchInfo.isSinglePhase', 'SwitchInfo.isUnganged'],
    asset_columns=['asset_mRID', 'IdentifiedObject.name', 'Asset.ProductAssetModel', 'Asset.inUseDate',
                   'Asset.AssetInfo'],
    operational_limit_set_columns=['operationallimitSet_mRID', 'IdentifiedObject.name',
                                   'OperationalLimitSet.Terminal'],
    # FIXME
    # вот тут у меня загвоздка в том что у набора может быть сколь угодно пределов по току и напряжению как
    # правило 5+2, а может и 5+4 разные по величине и длительности
    # предлагаю только этот класс парсить полностью сколько есть тегов, и потом их приджойнивать,
    # потому что их перед выгрузкой в таблицу красиво надо как-то сравнивать
    current_limit_columns=['currentlimit_mRID', 'OperationalLimit.OperationalLimitSet', 'IdentifiedObject.name',
                           'CurrentLimit.value', 'OperationalLimit.OperationalLimitType',
                           'OperationalLimit.LimitDependencyModel'],
    voltage_limit_columns=['voltageLimit_mRID', 'OperationalLimit.OperationalLimitSet', 'IdentifiedObject.name',
                           'VoltageLimit.value', 'OperationalLimit.OperationalLimitType'],

    bay_columns=['bay_mRID', 'IdentifiedObject.name', 'Bay.VoltageLevel'],
    voltage_level_columns=['voltagelevel_mRID', 'VoltageLevel.BaseVoltage', 'IdentifiedObject.name',
                           'VoltageLevel.Substation'],
    substation_columns=['substation_mRID', 'IdentifiedObject.name', 'Substation.Region'],
    manufacturer_columns=['manufacturer_mRID', 'IdentifiedObject.name', 'OrganisationRole.Organisation'],
    organisation_columns=['organisation_mRID', 'IdentifiedObject.name'],
    product_asset_model_columns=['productassetmodel_mRID', 'IdentifiedObject.name',
                                 'ProductAssetModel.Manufacturer'],
    terminal_columns=['terminal_mRID', 'ACDCTerminal.sequenceNumber', 'IdentifiedObject.name',
                      'Terminal.ConductingEquipment', 'Terminal.ConnectivityNode',
                      'ACDCTerminal.OperationalLimitSet'],
    temperature_dependent_limit_table_columns=['temperaturedependentlimittable_mRID', 'IdentifiedObject.name',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_1',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_2',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_3',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_4',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_5',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_6',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_7',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_8',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_9',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_10',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_11',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_12',
                                               'TemperatureDependentLimitTable.TemperatureDependentLimitPoint_13'],
    temperature_dependent_limit_point_columns=['temperaturedependentlimitpoint_mRID',
                                               'TemperatureDependentLimitPoint.temperature',
                                               'TemperatureDependentLimitPoint.limitPercent'],
)
