from policyengine_us.model_api import *


class MassachusettsLIHEAPHeatingType(Enum):
    HEATING_OIL_AND_PROPANE = "Heating oil and Propane"
    NATURAL_GAS = "Natural Gas"
    KEROSENE = "Kerosene"
    ELECTRICITY = "Electricity"
    OTHER = "Other"
    NONE = "None"


class ma_liheap_heating_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = MassachusettsLIHEAPHeatingType
    default_value = MassachusettsLIHEAPHeatingType.ELECTRICITY
    label = "Massachusetts LIHEAP household's heating type"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download"

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        oil_or_propane = (heating_type == types.FUEL_OIL) | (
            heating_type == types.PROPANE
        )
        return select(
            [
                oil_or_propane,
                heating_type == types.NATURAL_GAS,
                heating_type == types.KEROSENE,
                (heating_type == types.ELECTRICITY) | (heating_type == types.SOLAR),
                heating_type == types.NONE,
            ],
            [
                MassachusettsLIHEAPHeatingType.HEATING_OIL_AND_PROPANE,
                MassachusettsLIHEAPHeatingType.NATURAL_GAS,
                MassachusettsLIHEAPHeatingType.KEROSENE,
                MassachusettsLIHEAPHeatingType.ELECTRICITY,
                MassachusettsLIHEAPHeatingType.NONE,
            ],
            default=MassachusettsLIHEAPHeatingType.OTHER,
        )
