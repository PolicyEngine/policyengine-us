from policyengine_us.model_api import *


class de_pension_exclusion_eligible_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Capital gains counted toward the Delaware pension exclusion basket"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
    reference = "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=6"

    def formula(person, period, parameters):
        # Capital losses are already deductible against AGI and should not
        # erase the exclusion on otherwise-eligible interest, dividend,
        # pension, and rental income. Floor at zero before the basket sum.
        return max_(0, person("capital_gains", period))
