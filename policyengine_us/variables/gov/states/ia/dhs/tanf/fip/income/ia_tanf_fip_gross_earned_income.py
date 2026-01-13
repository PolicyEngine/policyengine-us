from policyengine_us.model_api import *


class ia_tanf_fip_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP gross earned income"
    unit = USD
    definition_period = MONTH
    reference = "Iowa HHS FIP Income Manual Chapter 4-E"
    documentation = "https://hhs.iowa.gov/media/3970"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        # Include employment income and self-employment income
        person = spm_unit.members
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)

        total_earned = employment_income + self_employment_income
        return spm_unit.sum(total_earned)
