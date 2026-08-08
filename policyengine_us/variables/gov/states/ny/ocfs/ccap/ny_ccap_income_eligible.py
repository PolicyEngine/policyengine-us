from policyengine_us.model_api import *


class ny_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Income eligible for the New York Child Care Assistance Program"
    defined_for = StateCode.NY
    reference = (
        "https://dos.ny.gov/system/files/documents/2024/05/050124.pdf#page=12",
        "https://dos.ny.gov/system/files/documents/2024/05/050124.pdf#page=13",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.income
        income = spm_unit("ccdf_income", period)
        # SSL 410-u(2), 410-w(1), and 410-w(3) capped income at 300% of the
        # state income standard (modeled as the federal poverty guideline)
        # before October 1, 2023, and at 85% of the state median income from
        # that date.
        if p.smi_income_limit_in_effect:
            income_limit = spm_unit("hhs_smi", period) * p.income_limit_smi_rate
        else:
            income_limit = spm_unit("spm_unit_fpg", period) * p.income_limit_fpg_rate
        return income <= income_limit
