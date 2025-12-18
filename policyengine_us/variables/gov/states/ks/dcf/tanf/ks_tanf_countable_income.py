from policyengine_us.model_api import *


class ks_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-110",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm7110.htm",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # Per K.A.R. 30-4-110 and KEESM 7110:
        # Countable Income = Countable Earned Income + Unearned Income
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        deductions = spm_unit("ks_tanf_earned_income_deductions", period)
        countable_earned = max_(gross_earned - deductions, 0)
        return countable_earned + gross_unearned
