from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.snap.income.snap_income_standard_helpers import (
    snap_monthly_income_standard,
)


class meets_tanf_non_cash_net_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets net income test for TANF non-cash benefit"
    documentation = "Income eligibility (net income as a percent of the poverty line) for TANF non-cash benefit for SNAP BBCE"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.2#j_2",
        "https://www.law.cornell.edu/cfr/text/7/273.9#a_3_ii",
    )

    def formula(spm_unit, period, parameters):
        # Determine if the net income limit applies to the household.
        applies = parameters(period).gov.hhs.tanf.non_cash.income_limit.net_applies
        state = spm_unit.household("state_code_str", period)
        # Varies depending on if the household has elderly and disabled people.
        hheod = spm_unit("is_tanf_non_cash_hheod", period)
        net_limit_applies = where(
            hheod, applies.hheod[state], applies.non_hheod[state]
        ).astype(bool)
        net_income = spm_unit("snap_net_income", period)
        net_limit = parameters(period).gov.usda.snap.income.limit.net
        # The state's BBCE net test uses the federal SNAP net standard: the
        # FNS table built per 7 CFR 273.9(a)(3)(ii), including the separately
        # rounded-up increment above eight persons. It is compared against
        # the whole-dollar rounded net income; a raw ratio would deny
        # households exactly at the published standard.
        limit = snap_monthly_income_standard(spm_unit, period, parameters, net_limit)
        # Either the net limit doesn't apply or they pass it.
        return ~net_limit_applies | (net_income <= limit)
