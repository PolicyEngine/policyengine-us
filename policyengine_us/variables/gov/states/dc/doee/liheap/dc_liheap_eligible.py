from policyengine_us.model_api import *


class dc_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the DC LIHEAP"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = "https://doee.dc.gov/liheap"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.liheap
        state_median_income = spm_unit("hhs_smi", period)
        # The income concept is not clearly defined, assuming IRS gross income
        income = add(spm_unit, period, ["irs_gross_income"])
        smi_limit = state_median_income * p.smi_limit
        return income <= smi_limit
