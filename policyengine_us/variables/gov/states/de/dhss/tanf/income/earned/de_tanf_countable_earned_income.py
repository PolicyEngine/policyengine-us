from policyengine_us.model_api import *


class de_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008",
        "https://dhss.delaware.gov/wp-content/uploads/sites/11/dss/pdf/detanfstateplan2017.pdf#page=6",
    )
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Sum person-level earned income (with $90 + $30 + 1/3 applied)
        # Then subtract childcare at household level
        countable_earned_person = add(
            spm_unit, period, ["de_tanf_countable_earned_income_person"]
        )
        dependent_care = spm_unit("de_tanf_dependent_care_deduction", period)
        return max_(countable_earned_person - dependent_care, 0)
