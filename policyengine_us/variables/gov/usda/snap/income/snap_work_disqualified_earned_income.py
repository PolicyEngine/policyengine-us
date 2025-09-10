from policyengine_us.model_api import *


class snap_work_disqualified_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP work disqualified earned income"
    documentation = "Earned income from members disqualified for work requirement failures (counted in full with no deduction)"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_1"
    unit = USD

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_disqualified = person("snap_work_requirement_disqualified", period)
        
        # Per 273.11(c)(1), entire income of work requirement failures is counted
        # Convert annual income to monthly for SNAP calculations
        employment_income = person("employment_income", period.this_year) / 12
        self_employment_income = person("self_employment_income", period.this_year) / 12
        
        total_earned = spm_unit.sum(
            (employment_income + self_employment_income) * is_disqualified
        )
        
        return total_earned