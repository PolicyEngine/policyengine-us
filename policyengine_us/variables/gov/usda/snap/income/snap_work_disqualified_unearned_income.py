from policyengine_us.model_api import *


class snap_work_disqualified_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP work disqualified unearned income"
    documentation = "Unearned income from members disqualified for work requirement failures (counted in full)"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_1"
    unit = USD

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_disqualified = person("snap_work_requirement_disqualified", period)
        
        # Common unearned income sources (annual amounts converted to monthly)
        social_security = person("social_security", period)
        ssi = person("ssi", period)
        unemployment_compensation = person("unemployment_compensation", period)
        pension_income = person("taxable_pension_income", period)

        total_unearned = spm_unit.sum(
            (social_security + ssi + unemployment_compensation + pension_income) * is_disqualified
        )
        
        return total_unearned