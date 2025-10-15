"""
Connecticut TFA overall eligibility.
"""

from policyengine_us.model_api import *


class ct_tfa_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Connecticut TFA eligibility"
    definition_period = MONTH
    defined_for = StateCode.CT
    documentation = (
        "Overall eligibility for Connecticut Temporary Family Assistance (TFA) "
        "program, Connecticut's implementation of federal TANF. Requires meeting "
        "demographic, income, and resource requirements."
    )
    reference = (
        "Connecticut General Statutes Section 17b-112; "
        "Connecticut TANF State Plan 2024-2026; "
        "https://www.cga.ct.gov/current/pub/chap_319s.htm"
    )

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit(
            "ct_tfa_demographic_eligible", period.this_year
        )
        income_eligible = spm_unit("ct_tfa_income_eligible", period)
        resources_eligible = spm_unit(
            "ct_tfa_resources_eligible", period.this_year
        )

        return demographic_eligible & income_eligible & resources_eligible
