from policyengine_us.model_api import *


class pa_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF gross unearned income"
    documentation = "Total gross unearned income (Social Security, pensions, unemployment, support payments, etc.) for the SPM unit before any deductions."
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = "55 Pa. Code § 183.31, § 183.32"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # Count major unearned income sources
        social_security = person("social_security", period)
        unemployment_compensation = person("unemployment_compensation", period)
        # Use simplified unearned income calculation
        return spm_unit.sum(social_security + unemployment_compensation)
