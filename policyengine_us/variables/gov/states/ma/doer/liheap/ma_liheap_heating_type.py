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
    documentation = "Derived from the canonical heating_type input: fuel oil and propane share the heating oil and propane row; kerosene keeps its own row; wood, coal and other fuels are the other category; solar and UNSPECIFIED take the electricity row (the pre-canonical default); NONE stays NONE. Setting this directly is deprecated during the vocabulary migration and changes only the rate row: the expense cap still follows the canonical heating_type."
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download"

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        oil_or_propane = (heating_type == types.FUEL_OIL) | (
            heating_type == types.PROPANE
        )
        # UNSPECIFIED keeps the pre-canonical default of electricity.
        electricity = (
            (heating_type == types.ELECTRICITY)
            | (heating_type == types.SOLAR)
            | (heating_type == types.UNSPECIFIED)
        )
        # The chart's "Oil, Propane, Kerosene & Other" category.
        other = (
            (heating_type == types.WOOD)
            | (heating_type == types.COAL)
            | (heating_type == types.OTHER)
        )
        return select(
            [
                oil_or_propane,
                heating_type == types.NATURAL_GAS,
                heating_type == types.KEROSENE,
                electricity,
                heating_type == types.NONE,
                other,
            ],
            [
                MassachusettsLIHEAPHeatingType.HEATING_OIL_AND_PROPANE,
                MassachusettsLIHEAPHeatingType.NATURAL_GAS,
                MassachusettsLIHEAPHeatingType.KEROSENE,
                MassachusettsLIHEAPHeatingType.ELECTRICITY,
                MassachusettsLIHEAPHeatingType.NONE,
                MassachusettsLIHEAPHeatingType.OTHER,
            ],
            default=MassachusettsLIHEAPHeatingType.ELECTRICITY,
        )
