from policyengine_us.model_api import *


class snap_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP earned income"
    documentation = "Earned income for calculating the SNAP earned income deduction"
    reference = "https://www.law.cornell.edu/cfr/text/7/273.9#b_1"
    unit = USD

    def formula(spm_unit, period):
        person = spm_unit.members
        income = spm_unit("snap_earned_income_person", period)
        countable_earner = person("snap_countable_earner", period)
        employment_income = person("employment_income", period)
        full_employment_income = spm_unit.sum(
            where(countable_earner, employment_income, 0)
        )
        fraction = person("snap_work_requirement_income_proration_fraction", period)
        prorated_employment_income = spm_unit.sum(
            where(countable_earner, employment_income * fraction, 0)
        )
        return income - full_employment_income + prorated_employment_income
