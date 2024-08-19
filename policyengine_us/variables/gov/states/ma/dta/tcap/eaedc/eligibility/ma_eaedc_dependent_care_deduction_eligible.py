from policyengine_us.model_api import *


class ma_eaedc_dependent_care_deduction_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts EAEDC dependent care deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275#(B)"
    )

    def formula(spm_unit, period, parameters):
    # If earned income higher than income limit, then no dependent care expense deduction.
        gross_earned_income = add(spm_unit, period, ["ma_eaedc_earned_income"])
        income_limit = add(spm_unit, period, ["ma_eaedc_income_limit"])
        return gross_earned_income <= income_limit
