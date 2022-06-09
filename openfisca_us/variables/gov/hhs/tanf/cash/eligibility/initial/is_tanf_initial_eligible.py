from openfisca_us.model_api import *


class is_tanf_initial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Initial Economic Eligibility for TANF"
    documentation = "Whether the familiy meets the economic requirements for the Temporary Assistance for Needy Families program on application."

    def formula(spm_unit, period, parameters):
        ied = spm_unit("tanf_initial_employment_deduction", period)
        earned_income = spm_unit("tanf_gross_earned_income", period)
        unearned_income = spm_unit("tanf_gross_unearned_income", period)
        net_earned_income = earned_income + unearned_income - ied
        payment_level = spm_unit("tanf_max_amount", period)
        return net_earned_income <= payment_level
