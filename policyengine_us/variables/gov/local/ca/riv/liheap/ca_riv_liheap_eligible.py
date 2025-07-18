from policyengine_us.model_api import *


class ca_riv_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the California Riverside County LIHEAP"
    definition_period = YEAR
    defined_for = "in_riv"
    reference = "https://capriverside.org/utility-assistance-program"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.liheap
        state_median_income = spm_unit("hhs_smi", period)
        # The income concept is not clearly defined, assuming IRS gross income
        countable_income = spm_unit("ca_riv_liheap_countable_income", period)
        smi_limit = state_median_income * p.smi_limit
        return countable_income <= smi_limit
