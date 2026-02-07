from policyengine_us.model_api import *


class RILIHEAPHeatingType(Enum):
    DELIVERABLE = "Deliverable"  # Oil, propane, kerosene, wood, coal
    NATURAL_GAS = "Natural Gas"
    ELECTRIC = "Electric"
    HEAT_IN_RENT = "Heat in Rent"  # Heat included in rent


class ri_liheap_heating_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = RILIHEAPHeatingType
    default_value = RILIHEAPHeatingType.NATURAL_GAS
    label = "Rhode Island LIHEAP household heating type"
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = "https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf"
