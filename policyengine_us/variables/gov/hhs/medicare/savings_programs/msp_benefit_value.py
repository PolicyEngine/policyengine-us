from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicare.savings_programs.category.msp_category import (
    MSPCategory,
)


class msp_benefit_value(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Savings Program estimated monthly benefit value"
    definition_period = MONTH
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
    )
    defined_for = "msp_eligible"

    def formula(person, period, parameters):
        category = person("msp_category", period)

        # Get premiums (automatically disaggregated from annual to monthly)
        part_a_premium = person("base_part_a_premium", period)
        part_b_premium = person("base_part_b_premium", period)

        # Benefit depends on category:
        # QMB: Part A + Part B premiums (plus deductibles/copays, not modeled)
        # SLMB: Part B premium only
        # QI: Part B premium only
        is_qmb = category == MSPCategory.QMB
        is_slmb = category == MSPCategory.SLMB
        is_qi = category == MSPCategory.QI

        return (
            is_qmb * (part_a_premium + part_b_premium)
            + is_slmb * part_b_premium
            + is_qi * part_b_premium
        )
