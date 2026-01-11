from policyengine_us.model_api import *


class mn_mfip_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Minnesota MFIP due to income"
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/142G.02#stat.142G.02.42"
    )
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        # Per MN Stat. 142G.16, Subd. 1:
        # Countable income (with dependent care deduction) < Family Wage Level
        countable = spm_unit(
            "mn_mfip_countable_income_for_eligibility", period
        )
        family_wage_level = spm_unit("mn_mfip_family_wage_level", period)
        return countable < family_wage_level
