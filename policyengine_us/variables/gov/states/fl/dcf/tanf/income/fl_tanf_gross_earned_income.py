from policyengine_us.model_api import *


class fl_tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TANF gross earned income"
    unit = USD
    definition_period = MONTH
    reference = "Florida Administrative Code Rule 65A-4.209"
    documentation = "Total earned income before disregards, with specific exclusions for student earnings and WIOA income"

    def formula(spm_unit, period, parameters):
        # Sum employment and self-employment income across all SPM unit members
        employment = spm_unit("employment_income", period)
        self_employment = spm_unit("self_employment_income", period)

        return employment + self_employment
