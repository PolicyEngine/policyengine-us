from policyengine_us.model_api import *


class mn_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Minnesota MFIP due to income"
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G/pdf"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("mn_tanf_countable_income", period)
        family_wage_level = spm_unit("mn_tanf_family_wage_level", period)
        return countable_income < family_wage_level
