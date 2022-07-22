from openfisca_us.model_api import *


class is_tanf_continuous_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Continued Economic Eligibility for TANF"
    documentation = "Whether the familiy meets the economic requirements for the Temporary Assistance for Needy Families program after being approved."

    def formula(spm_unit, period, parameters):
        earned_income = spm_unit("tanf_gross_earned_income", period)
        unearned_income = spm_unit("tanf_gross_unearned_income", period)
        net_income = earned_income + unearned_income
        payment_level = spm_unit("tanf_max_amount", period)
        return net_income <= payment_level
