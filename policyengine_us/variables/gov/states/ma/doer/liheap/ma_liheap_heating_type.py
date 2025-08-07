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
