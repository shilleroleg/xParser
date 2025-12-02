from dataclasses import dataclass


@dataclass
class IdealBreaker:
    breaker_columns: list[str]
    breaker_info_columns: list[str]
    asset_columns: list[str]
    # operational_limit_set_columns: list[str]
    # current_limit_columns: list[str]
    # voltage_limit_columns: list[str]
    bay_columns: list[str]
    voltage_level_columns: list[str]
    substation_columns: list[str]
    manufacturer_columns: list[str]
    organisation_columns: list[str]
    product_asset_model_columns: list[str]
    terminal_columns: list[str]
    # temperature_dependent_limit_table_columns: list[str]
    # temperature_dependent_limit_point_columns: list[str]
    # решили не нужно, достаточно сравнивать уид в свойстве полюса (терминала)
    # connectivity_node_columns: list[str]


ideal_breaker = IdealBreaker(
    breaker_columns=['breaker_mRID', 'IdentifiedObject.name', 'Equipment.EquipmentContainer',
                     'PowerSystemResource.Assets', 'PowerSystemResource.AssetDatasheet',
                     'ConductingEquipment.Terminals', 'ConductingEquipment.Terminals_2',
                     'ConductingEquipment.BaseVoltage', 'Equipment.normallyInService',
                     'ConductingEquipment.isThreePhaseEquipment',
                     'Switch.ratedCurrent', 'ProtectedSwitch.breakingCapacity',
                     'Switch.normalOpen', 'Breaker.inTransitTime', 'Switch.differenceInTransitTime',
                     'Equipment.OperationalLimitSet', 'Equipment.OperationalLimitSet_2'],
    # Группа 1
    bay_columns=['bay_mRID', 'IdentifiedObject.name', 'Bay.VoltageLevel'],
    voltage_level_columns=['voltagelevel_mRID', 'VoltageLevel.BaseVoltage', 'IdentifiedObject.name',
                           'VoltageLevel.Substation'],
    substation_columns=['substation_mRID', 'IdentifiedObject.name', 'Substation.Region'],
    # Группа 2
    asset_columns=['asset_mRID', 'IdentifiedObject.name', 'Asset.ProductAssetModel', 'Asset.inUseDate',
                   'Asset.AssetInfo'],
    product_asset_model_columns=['productassetmodel_mRID', 'IdentifiedObject.name', 'ProductAssetModel.Manufacturer'],
    manufacturer_columns=['manufacturer_mRID', 'IdentifiedObject.name', 'OrganisationRole.Organisation'],
    organisation_columns=['organisation_mRID', 'IdentifiedObject.name'],
    breaker_info_columns=['breakerinfo_mRID', 'IdentifiedObject.name', 'SwitchInfo.ratedVoltage',
                          'SwitchInfo.ratedCurrent',
                          'SwitchInfo.breakingCapacity', 'BreakerInfo.interruptingTime', 'BreakerInfo.ratedRecloseTime',
                          'SwitchInfo.ratedInterruptingTime', 'SwitchInfo.ratedInTransitTime',
                          'SwitchInfo.isSinglePhase', 'SwitchInfo.isUnganged'],
    # Группа 3
    terminal_columns=['terminal_mRID', 'ACDCTerminal.sequenceNumber', 'IdentifiedObject.name',
                      'Terminal.ConductingEquipment', 'Terminal.ConnectivityNode', 'ACDCTerminal.OperationalLimitSet'],
)
