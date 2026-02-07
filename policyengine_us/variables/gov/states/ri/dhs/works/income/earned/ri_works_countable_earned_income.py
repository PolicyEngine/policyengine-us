from policyengine_us.model_api import *


class ri_works_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island Works countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/rhode-island/218-RICR-20-00-2.15",
        "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
    )
    defined_for = StateCode.RI

    def formula(spm_unit, period, parameters):
        # Per 218-RICR-20-00-2.15: $525 + 50% disregard applies per earner
        earned_after_disregard = add(
            spm_unit, period, ["ri_works_earned_income_after_disregard_person"]
        )
        # Per 218-RICR-20-00-2.15.5(B)(2): Dependent care deduction
        dependent_care = spm_unit("ri_works_dependent_care_deduction", period)
        return max_(earned_after_disregard - dependent_care, 0)
