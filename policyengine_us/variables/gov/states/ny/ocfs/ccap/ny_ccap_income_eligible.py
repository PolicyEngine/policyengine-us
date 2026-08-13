from policyengine_us.model_api import *


class ny_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Income eligible for the New York Child Care Assistance Program"
    defined_for = StateCode.NY
    reference = (
        "https://ocfs.ny.gov/main/policies/external/2022/adm/22-OCFS-ADM-18.pdf#page=6",
        "https://dos.ny.gov/system/files/documents/2024/05/050124.pdf#page=12",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.income
        income = spm_unit("ny_ccap_countable_income", period)
        # 18 NYCRR 415.1(k) defines the state income standard as the most
        # recent federal income official poverty line, so the state income
        # standard multiple applies directly to spm_unit_fpg. Social Services
        # Law 410-u(2), 410-w(1) and 410-w(3) set that multiple at 200%
        # through July 31, 2022 and 300% from August 1, 2022. 22-OCFS-ADM-18
        # applied the 85% state median income ceiling alongside it from the
        # same date, and it binds for larger families. The state income
        # standard limit lapsed on October 1, 2023, leaving the state median
        # income ceiling alone.
        fpg_limit = spm_unit("spm_unit_fpg", period) * p.income_limit_fpg_rate
        smi_limit = spm_unit("hhs_smi", period) * p.income_limit_smi_rate
        if p.income_limit_fpg_in_effect and p.income_limit_smi_in_effect:
            income_limit = min_(fpg_limit, smi_limit)
        elif p.income_limit_fpg_in_effect:
            income_limit = fpg_limit
        else:
            income_limit = smi_limit
        return income <= income_limit
