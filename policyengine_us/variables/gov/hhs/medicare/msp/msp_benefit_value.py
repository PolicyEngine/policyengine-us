from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicare.msp.category.msp_category import (
    MSPCategory,
)


class msp_benefit_value(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Savings Program monthly benefit value"
    definition_period = MONTH
    documentation = (
        "Monthly value of MSP benefits based on category. "
        "QMB covers Part A and B premiums. SLMB and QI cover Part B only."
    )
    reference = "https://www.cms.gov/medicare/costs/medicare-savings-programs"
    defined_for = "msp_eligible"

    def formula(person, period, parameters):
        category = person("msp_category", period)
        # Get annual premiums and convert to monthly
        part_a_premium = (
            person("base_part_a_premium", period.this_year) / MONTHS_IN_YEAR
        )
        part_b_premium = (
            person("base_part_b_premium", period.this_year) / MONTHS_IN_YEAR
        )
        is_qmb = category == MSPCategory.QMB
        is_slmb = category == MSPCategory.SLMB
        is_qi = category == MSPCategory.QI
        # QMB covers Part A + Part B; SLMB and QI cover Part B only
        return (
            is_qmb * (part_a_premium + part_b_premium)
            + is_slmb * part_b_premium
            + is_qi * part_b_premium
        )
